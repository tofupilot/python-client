from tofupilot import numeric_step


@numeric_step(name="second", low=10)
def test_second(step):
    step.set_result(16).set_comparator("LE")
