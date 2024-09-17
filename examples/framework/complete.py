from tofupilot import pass_fail_step, numeric_limit_step, conf

conf.set(procedure_id="FVT1", serial_number="123", part_number="3", revision="12")


@pass_fail_step()
def test_pass_fail(step):
    step.check_condition(True)


@numeric_limit_step(name="second", low=10)
def test_second(step):
    step.set_result(16).set_comparator("LE")


@numeric_limit_step(name="titi")
def test_third(step):
    step.set_result(9, "V").set_limits(10, 12).set_comparator("GELE")
