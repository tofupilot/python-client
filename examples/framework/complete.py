from tofupilot import numeric_step, conf

conf.set(procedure_id="FVT1", serial_number="123", part_number="3", revision="12")


def test_pass_fail():
    assert True


@numeric_step(name="second", low=10)
def test_second(step):
    step.measure(16).set_comparator("LE")


@numeric_step(name="titi")
def test_third(step):
    step.measure(9).set_units("V").set_limits(10, 12).set_comparator("GELE")
