from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from threading import Lock
from datetime import datetime, timezone
import functools
import tempfile
import os
import json
import time
from abc import ABC, abstractmethod

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item

from .utils import duration_to_iso, datetime_to_iso


# Configuration object
class Conf:
    def __init__(self):
        self.procedure_id: Optional[str] = None
        self.unit_under_test: Dict[str, Any] = {}

    def set(
        self,
        procedure_id: Optional[str] = None,
        serial_number: Optional[str] = None,
        part_number: Optional[str] = None,
        revision: Optional[str] = None,
    ) -> None:
        if procedure_id is not None:
            self.procedure_id = procedure_id
        if serial_number is not None:
            self.unit_under_test["serial_number"] = serial_number
        if part_number is not None:
            self.unit_under_test["part_number"] = part_number
        if revision is not None:
            self.unit_under_test["revision"] = revision
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
        self.procedure_id: Optional[str] = None  # To store the procedure ID
        self.unit_under_test: Dict[str, Any] = {}  # To store unit under test info
        self.session_start_time: Optional[float] = None  # To store session start time
        self.test_steps_lock = Lock()
        self.test_steps = []
        self.output_file = None

    def append_step(self, step_info: Dict[str, Any]) -> None:
        with self.test_steps_lock:
            self.test_steps.append(step_info)

    def pytest_sessionstart(self) -> None:
        """
        Called after the Session object has been created and before performing collection and entering the run test loop.
        """
        # Recording the session start time
        self.session_start_time = time.time()

    def pytest_runtest_setup(self, item: Item) -> None:
        """
        Called before each test item is run.
        """
        # Determine the script file name
        script_file_name = os.path.basename(item.fspath).split(".")[0]

        # Create the output file path using the script file name
        self.output_file = os.path.join(
            tempfile.gettempdir(), f"{script_file_name}.json"
        )

        # Start timing the test
        item.start_time = time.time()

        # Collect procedure_id and unit_under_test from conf if available
        if self.procedure_id is None:
            self.procedure_id = conf.procedure_id
            self.unit_under_test = conf.unit_under_test

        # If not set in conf, try to get from test class
        if self.procedure_id is None:
            cls = item.getparent(pytest.Class)
            if cls:
                self.procedure_id = getattr(cls.obj, "procedure_id", None)
                unit = getattr(cls.obj, "unit", None)
                if unit:
                    self.unit_under_test = {"serial_number": unit}

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
        duration = time.time() - item.start_time

        # Retrieve step_info from item.user_properties
        step_info: Dict[str, Any] = {}
        for name, value in item.user_properties:
            if name == "step_info":
                step_info = value
                break  # Found the step_info, no need to continue

        step_info["duration"] = duration_to_iso(duration)
        step_info["started_at"] = datetime_to_iso(
            datetime.fromtimestamp(item.start_time, tz=timezone.utc)
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
        Writes the test_report variable in a json file
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
        started_at = datetime_to_iso(
            datetime.fromtimestamp(
                self.session_start_time or session_end_time, tz=timezone.utc
            )
        )
        duration_iso = duration_to_iso(total_duration)

        if not self.procedure_id:
            raise ValueError(
                "No procedure ID provided. Ensure you call conf.set(procedure_id='your_procedure_id', serial_number='your_serial_number'). For detailed instructions, visit docs.tofupilot.com/clients/pytest."
            )
        if not self.unit_under_test:
            raise ValueError(
                "No serial number provided. Ensure you call conf.set(procedure_id='your_procedure_id', serial_number='your_serial_number'). For detailed instructions, visit docs.tofupilot.com/clients/pytest."
            )

        # At the end of the session, write out the test report
        test_report = {
            "procedure_id": self.procedure_id,
            "unit_under_test": self.unit_under_test,
            "run_passed": run_passed,  # Add the run_passed property
            "started_at": started_at,  # Add the started_at of the whole test
            "duration": duration_iso,  # Add the duration of the whole test
            "steps": self.test_steps,  # Include all collected test steps
        }

        # Write the test report to the dynamically determined output file
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(test_report, f, indent=4)
            print(f"Test report written to {self.output_file}")
        except IOError as e:
            raise RuntimeError(
                f"Failed to write report to {self.output_file}: {e}"
            ) from e


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
                    "value": step.result,
                    "limit": step.limit,
                }
            )

        step.request.node.user_properties.append(("step_info", step_info))

    wrapper.step_type = step_type  # Set step_type attribute
    return wrapper


def numeric_step(func: Callable[..., Any] = None, **kwargs: Any) -> Callable[..., Any]:
    return step_decorator(func, step_type="numeric", **kwargs)


def string_step(func: Callable[..., Any] = None, **kwargs: Any) -> Callable[..., Any]:
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
    elif comp == "NE":
        return (
            measurement != low
            if low is not None
            else measurement != high if high is not None else False
        )
    elif comp == "LT":
        return measurement < high if high is not None else False
    elif comp == "LE":
        return measurement <= high if high is not None else False
    elif comp == "GT":
        return measurement > low if low is not None else False
    elif comp == "GE":
        return measurement >= low if low is not None else False
    elif comp == "LTGT":
        return (low is not None and high is not None) and low < measurement < high
    elif comp == "LTGE":
        return (low is not None and high is not None) and low <= measurement < high
    elif comp == "LEGT":
        return (low is not None and high is not None) and low < measurement <= high
    elif comp == "LEGE":
        return (low is not None and high is not None) and low <= measurement <= high
    else:
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
    # Depending on the test function, we need to decide whether to provide a NumericStep or StringStep
    # This can be inferred from the test function annotations or could be specified explicitly

    # For simplicity, let's assume the test function has an attribute 'step_type' set by the decorator
    step_type = getattr(request.node.function, "step_type", "numeric")
    if step_type == "numeric":
        s = NumericStep()
    elif step_type == "string":
        s = StringStep()
    else:
        raise ValueError(f"Unknown step type: {step_type}")

    s.request = request  # Attach the request object to access the pytest item
    return s
