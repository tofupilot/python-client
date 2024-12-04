from __future__ import annotations
from typing import Any, Callable, Dict, Optional, List
from threading import Lock
from datetime import datetime, timezone, timedelta
import functools
import time
from abc import ABC, abstractmethod

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item

from .client import TofuPilotClient
from .models import SubUnit


# Configuration object
class Conf:
    def __init__(self):
        self.procedure_id: Optional[str] = None
        self.unit_under_test: Dict[str, Any] = {}
        self.sub_units: Optional[List[SubUnit]] = None
        self.report_variables: Optional[Dict[str, str]] = None
        self.attachments: Optional[List[str]] = None

    def set(
        self,
        procedure_id: Optional[str] = None,
        serial_number: Optional[str] = None,
        part_number: Optional[str] = None,
        revision: Optional[str] = None,
        batch_number: Optional[str] = None,
        sub_units: Optional[List[SubUnit]] = None,
        report_variables: Optional[Dict[str, str]] = None,
        attachments: Optional[List[str]] = None,
    ) -> None:
        if procedure_id is not None:
            self.procedure_id = procedure_id
        if serial_number is not None:
            self.unit_under_test["serial_number"] = serial_number
        if part_number is not None:
            self.unit_under_test["part_number"] = part_number
        if revision is not None:
            self.unit_under_test["revision"] = revision
        if batch_number is not None:
            self.unit_under_test["batch_number"] = batch_number
        if sub_units is not None:
            self.sub_units = sub_units
        if report_variables is not None:
            self.report_variables = report_variables
        if attachments is not None:
            self.attachments = attachments
        return self


# Create a global conf object
conf = Conf()


def pytest_addoption(parser: Parser) -> None:
    """
    Add a command-line option to enable the Test Pilot plugin.
    """
    parser.addoption("--tofupilot", action="store_true", help="Use Test Pilot plugin")


def pytest_configure(config: Config) -> None:
    """
    Configure pytest to use the Test Pilot plugin if the --tofupilot option is provided.
    """
    if config.getoption("--tofupilot"):
        config.pluginmanager.register(TestPilotPlugin(), "testpilotplugin")


class TestPilotPlugin:
    """
    The Test Pilot plugin class that integrates with pytest hooks to collect test data.
    """

    def __init__(self) -> None:
        self.session_start_time: Optional[float] = None  # To store session start time
        self.test_steps_lock = Lock()
        self.test_steps = []

    def append_step(self, step_info: Dict[str, Any]) -> None:
        """
        Thread-safely appends test step to the test_step list.
        """
        with self.test_steps_lock:
            self.test_steps.append(step_info)

    def pytest_sessionstart(self) -> None:
        """
        Called after the Session object has been created and before
        performing collection and entering the run test loop.
        """
        # Recording the session start time
        self.session_start_time = time.time()

    def pytest_runtest_setup(self, item: Item) -> None:
        """
        Called before each test item is run.
        """
        # Start timing the test
        item.start_time = time.time()

    def pytest_runtest_call(self, item: Item) -> None:
        """
        Execute the test function and handle exceptions.
        """
        try:
            # Run the actual test function
            item.runtest()
            item.outcome = True
        except Exception as e:  # pylint: disable=broad-exception-caught / W0718
            # If an exception occurs, mark the outcome as failed and store the exception
            item.outcome = False
            item.excinfo = e

    def pytest_runtest_teardown(self, item: Item) -> None:
        """
        Called after each test item is run, during the teardown phase.
        """
        # End timing the test
        duration_seconds = time.time() - item.start_time
        duration = timedelta(seconds=duration_seconds)

        # Retrieve step_info from item.user_properties
        step_info: Dict[str, Any] = {}
        for name, value in item.user_properties:
            if name == "step_info":
                step_info = value
                break  # Found the step_info, no need to continue

        step_info["duration"] = duration
        step_info["started_at"] = datetime.fromtimestamp(
            item.start_time, tz=timezone.utc
        )

        if step_info.get("name") is None:
            step_info["name"] = item.name

        # Determine if the step passed or failed based on item.outcome
        step_info["step_passed"] = item.outcome

        # Append the step information to the global test_steps list
        self.append_step(step_info)

    def pytest_sessionfinish(self) -> None:
        """
        Called after the entire test session finishes.
        Uploads the test report to TofuPilot's API.
        """
        # Compute whether all steps passed
        run_passed = all(step.get("step_passed", False) for step in self.test_steps)

        # Record the session end time
        session_end_time = time.time()

        # Calculate the total duration
        total_duration = session_end_time - (
            self.session_start_time or session_end_time
        )

        # Format the started_at and duration fields
        started_at = datetime.fromtimestamp(
            self.session_start_time or session_end_time, tz=timezone.utc
        )
        duration_td = timedelta(seconds=total_duration)

        # Prepare the steps
        steps = self.test_steps

        # Create the TofuPilot client
        try:
            client = TofuPilotClient()
            client.create_run(
                procedure_id=conf.procedure_id,
                unit_under_test=conf.unit_under_test,
                run_passed=run_passed,
                started_at=started_at,
                duration=duration_td,
                steps=steps,
                sub_units=conf.sub_units,
                report_variables=conf.report_variables,
                attachments=conf.attachments,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upload report: {e}") from e


# Abstract base class for Steps
class Step(ABC):
    """
    Abstract base class to represent a test step.
    """

    def __init__(self) -> None:
        self.name: Optional[str] = None
        self.comp: str = "EQ"
        self.step_passed: Optional[bool] = None
        self.request: Optional[FixtureRequest] = None  # Will be set by the fixture

    @abstractmethod
    def evaluate(self) -> None:
        pass

    def __call__(self) -> None:
        """
        Evaluate the step and raise an AssertionError if it failed.
        """
        self.evaluate()
        if not self.step_passed:
            raise AssertionError(f"Value '{self.result}' did not meet the criteria.")
        return self.step_passed

    def set_name(self, name: str) -> Step:
        """
        Set the name of the test step.
        """
        self.name = name
        return self  # Allow method chaining

    def set_comparator(self, comp: str) -> Step:
        """
        Set the comparator type for limit evaluation.
        """
        self.comp = comp
        return self  # Allow method chaining

    # Allow arbitrary attributes to be set dynamically
    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value  # Store attribute in the instance dictionary

    def __getattr__(self, name: str) -> Any:
        # Return None if the attribute is not found
        return self.__dict__.get(name, None)


class NumericStep(Step):
    """
    Class to represent a numeric limit test step.
    """

    def __init__(self) -> None:
        super().__init__()
        self.result: Optional[float] = None
        self.low_limit: Optional[float] = None
        self.high_limit: Optional[float] = None
        self.units: Optional[str] = None
        self.comp = "DEFAULT"

    def measure(self, result: float) -> NumericStep:
        """
        Set the numeric result of the measurement.
        """
        self.result = result
        return self  # Allow method chaining

    def set_limits(
        self, low: Optional[float] = None, high: Optional[float] = None
    ) -> NumericStep:
        """
        Set the lower and upper limits for a numeric measurement.
        """
        self.low_limit = low
        self.high_limit = high
        return self  # Allow method chaining

    def set_units(self, units: str) -> NumericStep:
        """
        Set the units of the measurement.
        """
        self.units = units
        return self  # Allow method chaining

    def evaluate(self) -> None:
        """
        Evaluate the numeric measurement against the limits.
        """
        self.step_passed = evaluate_numeric_limits(
            self.result, self.low_limit, self.high_limit, self.comp
        )

    def __call__(self) -> None:
        """
        Evaluate and assert the numeric measurement against the limits.
        """
        self.evaluate()
        if not self.step_passed:
            raise AssertionError(
                f"Measurement {self.result} {self.units} did not meet the criteria."
            )
        return self.step_passed


class StringStep(Step):
    """
    Class to represent a string limit test step.
    """

    def __init__(self) -> None:
        super().__init__()
        self.result: Optional[str] = None
        self.limit: Optional[str] = None
        self.comp = "EQ"

    def measure(self, result: str) -> StringStep:
        """
        Set the string result of the measurement.
        """
        self.result = result
        return self  # Allow method chaining

    def set_limit(self, limit: str) -> StringStep:
        """
        Set the limit for a string measurement.
        """
        self.limit = limit
        return self  # Allow method chaining

    def evaluate(self) -> None:
        """
        Evaluate the string measurement against the limit.
        """
        self.step_passed = evaluate_string_limit(self.result, self.limit, self.comp)

    def __call__(self) -> None:
        """
        Evaluate and assert the string measurement against the limit.
        """
        self.evaluate()
        if not self.step_passed:
            raise AssertionError(f"Value '{self.result}' did not meet the criteria.")
        return self.step_passed


def step_decorator(
    func: Callable[..., Any], step_type: str, **decorator_kwargs: Any
) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, step: Step, **kwargs: Any) -> None:
        if step_type == "numeric":
            step.set_limits(decorator_kwargs.get("low"), decorator_kwargs.get("high"))
            step.set_units(decorator_kwargs.get("units", ""))
            step.set_comparator(decorator_kwargs.get("comp", "DEFAULT"))
        elif step_type == "string":
            step.set_limit(decorator_kwargs.get("limit"))
            step.set_comparator(decorator_kwargs.get("comp", "EQ"))

        step.set_name(decorator_kwargs.get("name", func.__name__))

        func(*args, step=step, **kwargs)

        step_info = {
            "name": step.name,
            "step_passed": step.step_passed,
            "comparator": step.comp,
        }
        if step_type == "numeric":
            step_info.update(
                {
                    "measurement_value": step.result,
                    "measurement_unit": step.units,
                    "limit_low": step.low_limit,
                    "limit_high": step.high_limit,
                }
            )
        elif step_type == "string":
            step_info.update(
                {
                    "measurement_value": step.result,
                }
            )

        step.request.node.user_properties.append(("step_info", step_info))

    wrapper.step_type = step_type  # Set step_type attribute
    return wrapper


def numeric_step(func: Callable[..., Any], **kwargs: Any) -> Callable[..., Any]:
    return step_decorator(func, step_type="numeric", **kwargs)


def string_step(func: Callable[..., Any], **kwargs: Any) -> Callable[..., Any]:
    return step_decorator(func, step_type="string", **kwargs)


def evaluate_numeric_limits(
    measurement: Optional[float],
    low: Optional[float],
    high: Optional[float],
    comp: str,
) -> bool:
    """
    Evaluate whether a measurement is within specified limits using the comparator.
    """
    if measurement is None:
        return False  # Cannot evaluate without a measurement
    if low is None and high is None:
        return False  # Cannot evaluate without limits

    if comp == "DEFAULT":
        if low is not None and high is None:
            comp = "GE"
        elif low is None and high is not None:
            comp = "LE"
        else:
            comp = "LEGE"

    if comp == "EQ":
        return (
            measurement == low
            if low is not None
            else measurement == high if high is not None else False
        )
    if comp == "NE":
        return (
            measurement != low
            if low is not None
            else measurement != high if high is not None else False
        )
    if comp == "LT":
        return measurement < high if high is not None else False
    if comp == "LE":
        return measurement <= high if high is not None else False
    if comp == "GT":
        return measurement > low if low is not None else False
    if comp == "GE":
        return measurement >= low if low is not None else False
    if comp == "LTGT":
        return (low is not None and high is not None) and low < measurement < high
    if comp == "LTGE":
        return (low is not None and high is not None) and low <= measurement < high
    if comp == "LEGT":
        return (low is not None and high is not None) and low < measurement <= high
    if comp == "LEGE":
        return (low is not None and high is not None) and low <= measurement <= high
    raise ValueError(f"Unknown comparison operator for numeric value: {comp}")


def evaluate_string_limit(
    value: Optional[str],
    limit: Optional[str],
    comp: str,
) -> bool:
    """
    Evaluate whether a string value is within specified limits using the comparator.
    """
    if value is None:
        return False
    if limit is None:
        return True  # One may simply log a value without comparing it

    # Handle comparison logic
    if comp == "EQ":
        return value == limit
    elif comp == "NE":
        return value != limit
    elif comp == "CASESENSIT":
        return value == limit  # Same as EQ but explicitly case-sensitive
    elif comp == "IGNORECASE":
        return value.lower() == limit.lower()
    else:
        raise ValueError(f"Unknown comparison operator for string value: {comp}")


# Define the 'step' fixture to provide a Step instance to test functions
@pytest.fixture
def step(request: FixtureRequest) -> Step:
    # We need to decide whether to provide a NumericStep or StringStep
    # This can be inferred from the test function annotations or could be specified explicitly

    # Test function has an attribute 'step_type' set by the decorator
    step_type = getattr(request.node.function, "step_type", "numeric")
    if step_type == "numeric":
        s = NumericStep()
    elif step_type == "string":
        s = StringStep()
    else:
        raise ValueError(f"Unknown step type: {step_type}")

    s.request = request  # Attach the request object to access the pytest item
    return s
