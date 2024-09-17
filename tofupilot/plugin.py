import pytest
import time
import datetime
import json
import functools

# Global variable to store test steps data
test_steps = []


def pytest_addoption(parser):
    """
    Add a command-line option to enable the Test Pilot plugin.
    """
    parser.addoption("--use-tp", action="store_true", help="Use Test Pilot plugin")


def pytest_configure(config):
    """
    Configure pytest to use the Test Pilot plugin if the --use-tp option is provided.
    """
    if config.getoption("--use-tp"):
        config.pluginmanager.register(TestPilotPlugin(), "testpilotplugin")


class TestPilotPlugin:
    """
    The Test Pilot plugin class that integrates with pytest hooks to collect test data.
    """

    def __init__(self):
        self.procedure_id = None  # To store the procedure ID from the test suite
        self.unit_under_test = {}  # To store information about the unit under test

    def pytest_runtest_setup(self, item):
        """
        Called before each test item is run.
        """
        # Start timing the test
        item.start_time = time.time()

        # Collect procedure_id and unit from the test class if available
        cls = item.getparent(pytest.Class)
        if cls and self.procedure_id is None:
            self.procedure_id = getattr(cls.obj, "procedure_id", None)
            unit = getattr(cls.obj, "unit", None)
            if unit:
                self.unit_under_test = {"serial_number": unit}

    def pytest_runtest_call(self, item):
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

    def pytest_runtest_teardown(self, item):
        """
        Called after each test item is run, during the teardown phase.
        """
        # End timing the test
        duration = time.time() - item.start_time

        # Retrieve step_info from item.user_properties
        step_info = {}
        for name, value in item.user_properties:
            if name == "step_info":
                step_info = value
                break  # Found the step_info, no need to continue

        # Add duration and start time to step_info
        step_info["duration"] = str(datetime.timedelta(seconds=duration))
        step_info["started_at"] = datetime.datetime.fromtimestamp(
            item.start_time
        ).isoformat()

        # Determine if the step passed or failed based on item.outcome
        if getattr(item, "outcome", None) == "passed":
            step_info["step_passed"] = True
        else:
            step_info["step_passed"] = False

        # Append the step information to the global test_steps list
        test_steps.append(step_info)

    def pytest_sessionfinish(self, session, exitstatus):
        """
        Called after the entire test session finishes.
        Writes the test_report variable in a json file
        """
        # At the end of the session, write out the test_report.json
        test_report = {
            "procedure_id": self.procedure_id or "your_procedure_id",
            "unit_under_test": self.unit_under_test
            or {
                "serial_number": "your_serial_number",
                "part_number": "your_part_number",
            },
            "steps": test_steps,  # Include all collected test steps
        }
        # Write the test report to a JSON file
        with open("test_report.json", "w") as f:
            json.dump(test_report, f, indent=4)


def pass_fail_step(name=None):
    """
    Decorator for pass/fail test steps.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, step, **kwargs):
            # Set the step name
            step.name = name or func.__name__

            # Call the actual test function, passing the step object
            func(*args, step=step, **kwargs)

            # Evaluate the result stored in step.result
            step_passed = getattr(step, "result", False)

            # Prepare step_info with necessary details
            step_info = {
                "name": step.name,
                "step_passed": step_passed,
            }

            # Attach step_info to the pytest item object via user_properties
            step.request.node.user_properties.append(("step_info", step_info))

            # If the step failed, raise an AssertionError to mark the test as failed
            if not step_passed:
                raise AssertionError("Step failed.")

        return wrapper

    return decorator


def numeric_limit_step(func=None, **decorator_kwargs):
    """
    Decorator for numeric limit test steps, which can be used with or without arguments.
    """
    if func is not None and callable(func):
        # Decorator used without arguments
        @functools.wraps(func)
        def wrapper(*args, step, **kwargs):
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
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, step, **kwargs):
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


def evaluate_limits(measurement, low, high, comp):
    """
    Evaluate whether a measurement is within specified limits using the comparator.
    """
    if measurement is None:
        return False  # Cannot evaluate without a measurement
    if low is None and high is None:
        return False  # Cannot evaluate without limits

    # Perform the comparison based on the comparator type
    if comp == "GELE":
        return low <= measurement <= high
    elif comp == "LELE":
        return low < measurement < high
    elif comp == "GE":
        return measurement >= low
    elif comp == "LE":
        return measurement <= high
    else:
        # If an unknown comparator is provided, return False
        return False


class StepData:
    """
    Class to store and manage data related to a test step.
    """

    def __init__(self):
        pass  # No initialization needed for now

    def set_result(self, result, units=None):
        """
        Set the numeric result of a measurement, optionally specifying units.
        """
        self.result_numeric = result  # Store the measurement value
        if units:
            self.result_units = units  # Store the units if provided
        return self  # Allow method chaining

    def set_limits(self, low, high):
        """
        Set the lower and upper limits for a measurement.
        """
        self.limits_low = low
        self.limits_high = high
        return self  # Allow method chaining

    def set_comparator(self, comp):
        """
        Set the comparator type for limit evaluation.
        """
        self.comp = comp
        return self  # Allow method chaining

    def set_name(self, name):
        """
        Set the name of the test step.
        """
        self.name = name
        return self  # Allow method chaining

    def check_condition(self, condition):
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
    def __setattr__(self, name, value):
        self.__dict__[name] = value  # Store attribute in the instance dictionary

    def __getattr__(self, name):
        # Return None if the attribute is not found
        return self.__dict__.get(name, None)


def test_suite(procedure_id=None, unit=None):
    """
    Decorator for test classes to attach procedure ID and unit information.
    """

    def decorator(cls):
        cls.procedure_id = procedure_id  # Attach procedure_id to the class
        cls.unit = unit  # Attach unit information to the class
        return cls

    return decorator


# Define the 'step' fixture to provide a StepData instance to test functions
@pytest.fixture
def step(request):
    s = StepData()
    s.request = request  # Attach the request object to access the pytest item
    return s
