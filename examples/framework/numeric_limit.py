from tofupilot import conf, numeric_step

conf.set(procedure_id="FVT1", serial_number="123")


@numeric_step(name="second", low=10)
def test_second(step):
    step.measure(16).set_comparator("LE")
