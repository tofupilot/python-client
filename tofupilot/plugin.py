from __future__ import annotations

from datetime import datetime, timedelta, timezone
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
        self.session_start_time: Optional[float] = None  # To store session start time

    def pytest_sessionstart(self, session: Session) -> None:
        """
        Called after the Session object has been created and before performing collection and entering the run test loop.
        """
        # Record the session start time
        self.session_start_time = time.time()

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
            item.outcome = True
        except Exception as e:
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
        test_steps.append(step_info)

    def pytest_sessionfinish(self, session: Session, exitstatus: int) -> None:
        """
        Called after the entire test session finishes.
        Writes the test_report variable in a json file
        """
        # Compute whether all steps passed
        run_passed = all(step.get("step_passed", False) for step in test_steps)

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

        # At the end of the session, write out the test report
        test_report = {
            "procedure_id": self.procedure_id or "your_procedure_id",
            "unit_under_test": self.unit_under_test
            or {
                "serial_number": "your_serial_number",
                "part_number": "your_part_number",
            },
            "run_passed": run_passed,  # Add the run_passed property
            "started_at": started_at,  # Add the started_at of the whole test
            "duration": duration_iso,  # Add the duration of the whole test
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
            step_passed = evaluate_numeric_limits(
                measurement, low_limit, high_limit, comp
            )

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
                step_passed = evaluate_numeric_limits(
                    measurement, low_limit, high_limit, comp
                )

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


def string_value_step(
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
            value = getattr(step, "result_string", None)
            limit = getattr(step, "limits_low", None)
            comp = getattr(step, "comp", "EQ")
            name = getattr(step, "name", func.__name__)

            # Evaluate whether the measurement is within limits
            step_passed = evaluate_string_limit(value, limit, comp)

            # Prepare step_info with measurement details
            step_info = {
                "name": name,
                "value": value,
                "limit": limit,
                "comparator": comp,
                "step_passed": step_passed,
            }

            # Attach step_info to the pytest item object
            step.request.node.user_properties.append(("step_info", step_info))

            # If the step failed, raise an AssertionError with a descriptive message
            if not step_passed:
                raise AssertionError(f"Value {value} is outside limit.")

        return wrapper
    else:
        # Decorator used with arguments
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(*args: Any, step: "StepData", **kwargs: Any) -> None:
                # Set parameters from decorator arguments before calling the test function
                step.limit = decorator_kwargs.get("limit")
                step.comp = decorator_kwargs.get("comp", "EQ")
                step.name = decorator_kwargs.get("name", func.__name__)

                # Call the actual test function
                func(*args, step=step, **kwargs)

                # Retrieve values from step after the test function executes
                value = getattr(step, "result_string", None)
                limit = getattr(step, "limit", None)
                comp = getattr(step, "comp", "GELE")
                name = getattr(step, "name", func.__name__)

                # Evaluate whether the measurement is within limits
                step_passed = evaluate_string_limit(value, limit, comp)

                # Prepare step_info with measurement details
                step_info = {
                    "name": name,
                    "value": value,
                    "limit": limit,
                    "comparator": comp,
                    "step_passed": step_passed,
                }

                # Attach step_info to the pytest item object
                step.request.node.user_properties.append(("step_info", step_info))

                # If the step failed, raise an AssertionError with a descriptive message
                if not step_passed:
                    raise AssertionError(f"Value {value} is outside limit.")

            return wrapper

        return decorator


def evaluate_numeric_limits(
    measurement: Optional[float],
    low: Optional[float],
    high: Optional[float],
    comp: str,
) -> bool:
    """
    Evaluate whether a measurement is within specified limits using the comparator.

    Comparators:
    - 'EQ': True if measurement equals low.
    - 'NE': True if measurement does not equal low.
    - 'LT': True if measurement is less than low.
    - 'LE': True if measurement is less than or equal to low.
    - 'GT': True if measurement is greater than high.
    - 'GE': True if measurement is greater than or equal to high.
    - 'LTGT': True if low < measurement < high.
    - 'LTGE': True if low < measurement <= high.
    - 'LEGT': True if low <= measurement < high.
    - 'LEGE': True if low <= measurement <= high.
    - 'GTLT': True if high < measurement < low (swapped range).
    - 'GTLE': True if high < measurement <= low (swapped range).
    - 'GELT': True if high <= measurement < low (swapped range).
    - 'GELE': True if high <= measurement <= low (swapped range).

    If measurement is None, return False. If both limits are None, return False.
    """
    if measurement is None:
        return False  # Cannot evaluate without a measurement
    if low is None and high is None:
        return False  # Cannot evaluate without limits

    if comp == "EQ":
        return measurement == low
    elif comp == "NE":
        return measurement != low
    elif comp == "LT":
        return measurement < low if low is not None else False
    elif comp == "LE":
        return measurement <= low if low is not None else False
    elif comp == "GT":
        return measurement > high if high is not None else False
    elif comp == "GE":
        return measurement >= high if high is not None else False
    elif comp == "LTGT":
        return (low is not None and high is not None) and low < measurement < high
    elif comp == "LTGE":
        return (low is not None and high is not None) and low < measurement <= high
    elif comp == "LEGT":
        return (low is not None and high is not None) and low <= measurement < high
    elif comp == "LEGE":
        return (low is not None and high is not None) and low <= measurement <= high
    elif comp == "GTLT":
        return (low is not None and high is not None) and high < measurement < low
    elif comp == "GTLE":
        return (low is not None and high is not None) and high < measurement <= low
    elif comp == "GELT":
        return (low is not None and high is not None) and high <= measurement < low
    elif comp == "GELE":
        return (low is not None and high is not None) and high <= measurement <= low
    else:
        raise ValueError(f"Unknown comparison operator for numeric value: {comp}")


def evaluate_string_limit(
    value: Optional[str],
    limit: Optional[str],
    comp: str,
) -> bool:
    """
    Evaluate whether a string value is within specified limits using the comparator.
    Comparators:
    - 'EQ': True if value equals limit (case-sensitive)
    - 'NE': True if value does not equal limit (case-sensitive)
    - 'CASESENSIT': True if value exactly equals limit (case-sensitive)
    - 'IGNORECASE': True if value equals limit (case-insensitive)

    If value or limit is None, return False.
    """
    if value is None or limit is None:
        return False  # Cannot evaluate without value and limit

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


class StepData:
    """
    Class to store and manage data related to a test step.
    """

    def __init__(self) -> None:
        pass  # No initialization needed for now

        from typing import Union, Optional

    def set_result(
        self, result: Union[float, str], units: Optional[str] = None
    ) -> StepData:
        """
        Set the result of a measurement. If result is a float, update result_numeric.
        If result is a string, update result_step. Optionally specify units.
        """
        if isinstance(result, float):
            self.result_numeric = result  # Store the numeric result
        elif isinstance(result, str):
            self.result_string = result  # Store the string result
        else:
            raise ValueError("Result must be either a float or a string")

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


# Define the 'step' fixture to provide a StepData instance to test functions
@pytest.fixture
def step(request: FixtureRequest) -> StepData:
    s = StepData()
    s.request = request  # Attach the request object to access the pytest item
    return s
