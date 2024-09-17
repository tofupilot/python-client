import pytest
import time
import datetime
import json
import functools

# Global variable to store test steps data
test_steps = []


def pytest_addoption(parser):
    parser.addoption("--use-tp", action="store_true", help="Use Test Pilot plugin")


def pytest_configure(config):
    if config.getoption("--use-tp"):
        config.pluginmanager.register(TestPilotPlugin(), "testpilotplugin")


class TestPilotPlugin:
    def __init__(self):
        self.procedure_id = None
        self.unit_under_test = {}

    def pytest_runtest_setup(self, item):
        # Start timing the test
        item.start_time = time.time()

        # Collect procedure_id and unit from the class if available
        cls = item.getparent(pytest.Class)
        if cls and self.procedure_id is None:
            self.procedure_id = getattr(cls.obj, "procedure_id", None)
            unit = getattr(cls.obj, "unit", None)
            if unit:
                self.unit_under_test = {"serial_number": unit}

    def pytest_runtest_call(self, item):
        # Execute the test function and handle exceptions
        try:
            item.runtest()
            item.outcome = "passed"
        except Exception as e:
            item.outcome = "failed"
            item.excinfo = e

    def pytest_runtest_teardown(self, item):
        # End timing the test
        duration = time.time() - item.start_time

        # Collect test result information
        step_info = getattr(item.obj, "step_info", {})
        step_info["duration"] = str(datetime.timedelta(seconds=duration))
        step_info["started_at"] = datetime.datetime.fromtimestamp(
            item.start_time
        ).isoformat()

        # Determine if the step passed or failed
        if getattr(item, "outcome", None) == "passed":
            step_info["step_passed"] = True
        else:
            step_info["step_passed"] = False

        # Append the step information to test_steps
        test_steps.append(step_info)

    def pytest_sessionfinish(self, session, exitstatus):
        # At the end of the session, write out the test_report.json
        test_report = {
            "procedure_id": self.procedure_id or "your_procedure_id",
            "unit_under_test": self.unit_under_test
            or {
                "serial_number": "your_serial_number",
                "part_number": "your_part_number",
            },
            "steps": test_steps,
        }
        with open("test_report.json", "w") as f:
            json.dump(test_report, f, indent=4)


def pass_fail_step(name=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, step, **kwargs):
            func(*args, step=step, **kwargs)

            # Evaluate the result
            step_passed = getattr(step, "result", False)

            # Store the result in step_info
            step_info = {
                "name": name or func.__name__,
                "step_passed": step_passed,
                # Include additional information if needed
            }
            func.step_info = step_info

            if not step_passed:
                raise AssertionError("Step failed.")

        wrapper.step_info = {}
        return wrapper

    return decorator


def numeric_limit_step(func=None, **decorator_kwargs):
    if func is not None and callable(func):
        # Decorator used without arguments
        @functools.wraps(func)
        def wrapper(*args, step, **kwargs):
            func(*args, step=step, **kwargs)

            # After the function call, get values from step
            measurement = getattr(step, "result_numeric", None)
            units = getattr(step, "result_units", None)
            low_limit = getattr(step, "limits_low", None)
            high_limit = getattr(step, "limits_high", None)
            comp = getattr(step, "comp", "GELE")
            name = getattr(step, "name", func.__name__)

            step_passed = evaluate_limits(measurement, low_limit, high_limit, comp)

            # Store result in step_info
            step_info = {
                "name": name,
                "measurement_value": measurement,
                "measurement_unit": units,
                "limit_low": low_limit,
                "limit_high": high_limit,
                "comparator": comp,
                "step_passed": step_passed,
            }
            func.step_info = step_info

            if not step_passed:
                raise AssertionError(
                    f"Measurement {measurement} {units} is outside limits."
                )

        wrapper.step_info = {}
        return wrapper
    else:
        # Decorator used with arguments
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, step, **kwargs):
                # Set parameters from decorator arguments
                step.limits_low = decorator_kwargs.get("low")
                step.limits_high = decorator_kwargs.get("high")
                step.result_units = decorator_kwargs.get("units")
                step.comp = decorator_kwargs.get("comp", "GELE")
                step.name = decorator_kwargs.get("name", func.__name__)

                func(*args, step=step, **kwargs)

                # Evaluate the result
                measurement = getattr(step, "result_numeric", None)
                units = getattr(step, "result_units", None)
                low_limit = getattr(step, "limits_low", None)
                high_limit = getattr(step, "limits_high", None)
                comp = getattr(step, "comp", "GELE")
                name = getattr(step, "name", func.__name__)

                step_passed = evaluate_limits(measurement, low_limit, high_limit, comp)

                # Store result in step_info
                step_info = {
                    "name": name,
                    "measurement_value": measurement,
                    "measurement_unit": units,
                    "limit_low": low_limit,
                    "limit_high": high_limit,
                    "comparator": comp,
                    "step_passed": step_passed,
                }
                func.step_info = step_info

                if not step_passed:
                    raise AssertionError(
                        f"Measurement {measurement} {units} is outside limits."
                    )

            wrapper.step_info = {}
            return wrapper

        return decorator


def evaluate_limits(measurement, low, high, comp):
    if measurement is None:
        return False
    if low is None and high is None:
        return False  # Cannot evaluate without limits
    if comp == "GELE":
        return low <= measurement <= high
    elif comp == "LELE":
        return low < measurement < high
    elif comp == "GE":
        return measurement >= low
    elif comp == "LE":
        return measurement <= high
    # Add more comparison types as needed
    else:
        return False


class StepData:
    def __init__(self):
        pass

    def set_result(self, result, units=None):
        self.result_numeric = result
        if units:
            self.result_units = units
        return self  # Allow method chaining

    def set_limits(self, low, high):
        self.limits_low = low
        self.limits_high = high
        return self  # Allow method chaining

    def set_comparator(self, comp):
        self.comp = comp
        return self  # Allow method chaining

    def set_name(self, name):
        self.name = name
        return self  # Allow method chaining

    def check_condition(self, condition_func):
        self.result = condition_func()

    # Allow arbitrary attributes to be set dynamically
    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getattr__(self, name):
        return self.__dict__.get(name, None)


def test_suite(procedure_id=None, unit=None):
    def decorator(cls):
        cls.procedure_id = procedure_id
        cls.unit = unit
        return cls

    return decorator


# Define the 'step' fixture
@pytest.fixture
def step():
    return StepData()
