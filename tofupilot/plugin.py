from __future__ import annotations

from datetime import datetime
from .utils import duration_to_iso, datetime_to_iso
import functools
import json
import os
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.nodes import Item

# Global variable to store test steps data
test_steps: List[Dict[str, Any]] = []


# Configuration object
class Conf:
    def __init__(self):
        self.procedure_id: Optional[str] = None
        self.unit_under_test: Dict[str, Any] = {}
        self.output_file: str = "test_report.json"  # Default output file name

    def set(
        self,
        procedure_id: Optional[str] = None,
        serial_number: Optional[str] = None,
        part_number: Optional[str] = None,
        revision: Optional[str] = None,
        output_file: Optional[str] = None,
    ) -> None:
        if procedure_id is not None:
            self.procedure_id = procedure_id
        if serial_number is not None:
            self.unit_under_test["serial_number"] = serial_number
        if part_number is not None:
            self.unit_under_test["part_number"] = part_number
        if revision is not None:
            self.unit_under_test["revision"] = revision
        if output_file is not None:
            self.output_file = output_file


# Create a global conf object
conf = Conf()


def pytest_addoption(parser: Parser) -> None:
    """
    Add a command-line option to enable the Test Pilot plugin.
    """
    parser.addoption("--use-tp", action="store_true", help="Use Test Pilot plugin")


def pytest_configure(config: Config) -> None:
    """
    Configure pytest to use the Test Pilot plugin if the --use-tp option is provided.
    """
    if config.getoption("--use-tp"):
        config.pluginmanager.register(TestPilotPlugin(), "testpilotplugin")


class TestPilotPlugin:
    """
    The Test Pilot plugin class that integrates with pytest hooks to collect test data.
    """

    def __init__(self) -> None:
        self.procedure_id: Optional[str] = None  # To store the procedure ID
        self.unit_under_test: Dict[str, Any] = {}  # To store unit under test info
        self.output_file: str = conf.output_file  # Get output file from conf

    def pytest_runtest_setup(self, item: Item) -> None:
        """
        Called before each test item is run.
        """
        # Start timing the test
        item.start_time = time.time()

        # Collect procedure_id and unit_under_test from conf if available
        if self.procedure_id is None:
            self.procedure_id = conf.procedure_id
            self.unit_under_test = conf.unit_under_test
            self.output_file = conf.output_file  # Update output_file from conf

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
            item.outcome = "passed"
        except Exception as e:
            # If an exception occurs, mark the outcome as failed and store the exception
            item.outcome = "failed"
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
            datetime.fromtimestamp(item.start_time)
        )

        if step_info.get("name") is None:
            step_info["name"] = item.name

        # Determine if the step passed or failed based on item.outcome
        step_info["step_passed"] = item.outcome == "passed"

        # Append the step information to the global test_steps list
        test_steps.append(step_info)

    def pytest_sessionfinish(self, session: Session, exitstatus: int) -> None:
        """
        Called after the entire test session finishes.
        Writes the test_report variable in a json file
        """
        # At the end of the session, write out the test report
        test_report = {
            "procedure_id": self.procedure_id or "your_procedure_id",
            "unit_under_test": self.unit_under_test
            or {
                "serial_number": "your_serial_number",
                "part_number": "your_part_number",
            },
            "steps": test_steps,  # Include all collected test steps
        }

        # Create directory if it does not exist
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the test report to the specified output file
        with open(self.output_file, "w") as f:
            json.dump(test_report, f, indent=4)


def numeric_limit_step(
    func: Optional[Callable[..., Any]] = None, **decorator_kwargs: Any
) -> Callable[..., Any]:
    """
    Decorator for numeric limit test steps, which can be used with or without arguments.
    """
    if func is not None and callable(func):
        # Decorator used without arguments
        @functools.wraps(func)
        def wrapper(*args: Any, step: "StepData", **kwargs: Any) -> None:
            # Call the actual test function
            func(*args, step=step, **kwargs)

            # Retrieve values from step after the test function executes
            measurement = getattr(step, "result_numeric", None)
            units = getattr(step, "result_units", "")
            low_limit = getattr(step, "limits_low", None)
            high_limit = getattr(step, "limits_high", None)
            comp = getattr(step, "comp", "GELE")
            name = getattr(step, "name", func.__name__)

            # Evaluate whether the measurement is within limits
            step_passed = evaluate_limits(measurement, low_limit, high_limit, comp)

            # Prepare step_info with measurement details
            step_info = {
                "name": name,
                "measurement_value": measurement,
                "measurement_unit": units,
                "limit_low": low_limit,
                "limit_high": high_limit,
                "comparator": comp,
                "step_passed": step_passed,
            }

            # Attach step_info to the pytest item object
            step.request.node.user_properties.append(("step_info", step_info))

            # If the step failed, raise an AssertionError with a descriptive message
            if not step_passed:
                raise AssertionError(
                    f"Measurement {measurement} {units} is outside limits."
                )

        return wrapper
    else:
        # Decorator used with arguments
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(*args: Any, step: "StepData", **kwargs: Any) -> None:
                # Set parameters from decorator arguments before calling the test function
                step.limits_low = decorator_kwargs.get("low")
                step.limits_high = decorator_kwargs.get("high")
                step.result_units = decorator_kwargs.get("units", "")
                step.comp = decorator_kwargs.get("comp", "GELE")
                step.name = decorator_kwargs.get("name", func.__name__)

                # Call the actual test function
                func(*args, step=step, **kwargs)

                # Retrieve values from step after the test function executes
                measurement = getattr(step, "result_numeric", None)
                units = getattr(step, "result_units", "")
                low_limit = getattr(step, "limits_low", None)
                high_limit = getattr(step, "limits_high", None)
                comp = getattr(step, "comp", "GELE")
                name = getattr(step, "name", func.__name__)

                # Evaluate whether the measurement is within limits
                step_passed = evaluate_limits(measurement, low_limit, high_limit, comp)

                # Prepare step_info with measurement details
                step_info = {
                    "name": name,
                    "measurement_value": measurement,
                    "measurement_unit": units,
                    "limit_low": low_limit,
                    "limit_high": high_limit,
                    "comparator": comp,
                    "step_passed": step_passed,
                }

                # Attach step_info to the pytest item object
                step.request.node.user_properties.append(("step_info", step_info))

                # If the step failed, raise an AssertionError with a descriptive message
                if not step_passed:
                    raise AssertionError(
                        f"Measurement {measurement} {units} is outside limits."
                    )

            return wrapper

        return decorator


def evaluate_limits(
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

    # Perform the comparison based on the comparator type (standard TestStand comparison type)
    if comp == "EQ":
        return low is not None and measurement == low
    elif comp == "NE":
        return low is not None and measurement != low
    elif comp == "GELE":
        return (low is None or measurement >= low) and (
            high is None or measurement <= high
        )
    elif comp == "GTLT":
        return (low is None or measurement > low) and (
            high is None or measurement < high
        )
    elif comp == "GELT":
        return (low is None or measurement >= low) and (
            high is None or measurement < high
        )
    elif comp == "GTLE":
        return (low is None or measurement > low) and (
            high is None or measurement <= high
        )
    elif comp == "LTGT":
        return (low is not None and measurement < low) or (
            high is not None and measurement > high
        )
    elif comp == "LEGE":
        return (low is not None and measurement <= low) or (
            high is not None and measurement >= high
        )
    elif comp == "LEGT":
        return (low is not None and measurement <= low) or (
            high is not None and measurement > high
        )
    elif comp == "LTGE":
        return (low is not None and measurement < low) or (
            high is not None and measurement >= high
        )
    elif comp == "GT":
        return low is not None and measurement > low
    elif comp == "LT":
        return high is not None and measurement < high
    elif comp == "GE":
        return low is not None and measurement >= low
    elif comp == "LE":
        return high is not None and measurement <= high

    else:
        # If an unknown comparator is provided, return False
        return False


class StepData:
    """
    Class to store and manage data related to a test step.
    """

    def __init__(self) -> None:
        pass  # No initialization needed for now

    def set_result(self, result: float, units: Optional[str] = None) -> StepData:
        """
        Set the numeric result of a measurement, optionally specifying units.
        """
        self.result_numeric = result  # Store the measurement value
        if units:
            self.result_units = units  # Store the units if provided
        return self  # Allow method chaining

    def set_limits(self, low: float, high: float) -> StepData:
        """
        Set the lower and upper limits for a measurement.
        """
        self.limits_low = low
        self.limits_high = high
        return self  # Allow method chaining

    def set_comparator(self, comp: str) -> StepData:
        """
        Set the comparator type for limit evaluation.
        """
        self.comp = comp
        return self  # Allow method chaining

    def set_name(self, name: str) -> StepData:
        """
        Set the name of the test step.
        """
        self.name = name
        return self  # Allow method chaining

    def check_condition(self, condition: Union[Callable[[], bool], bool]) -> None:
        """
        Evaluate a pass/fail condition, which can be a callable or a boolean value.
        """
        if callable(condition):
            # If condition is a callable (e.g., a lambda), call it to get the result
            self.result = condition()
        else:
            # If condition is a direct value, convert it to a boolean
            self.result = bool(condition)

    # Allow arbitrary attributes to be set dynamically
    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value  # Store attribute in the instance dictionary

    def __getattr__(self, name: str) -> Any:
        # Return None if the attribute is not found
        return self.__dict__.get(name, None)


def test_suite(
    procedure_id: Optional[str] = None, unit: Optional[str] = None
) -> Callable[[Type], Type]:
    """
    Decorator for test classes to attach procedure ID and unit information.
    """

    def decorator(cls: Type) -> Type:
        cls.procedure_id = procedure_id  # Attach procedure_id to the class
        cls.unit = unit  # Attach unit information to the class
        return cls

    return decorator


# Define the 'step' fixture to provide a StepData instance to test functions
@pytest.fixture
def step(request: FixtureRequest) -> StepData:
    s = StepData()
    s.request = request  # Attach the request object to access the pytest item
    return s
