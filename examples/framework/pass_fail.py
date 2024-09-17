from tofupilot import pass_fail_step


@pass_fail_step()
def test_pass_fail(step):
    step.check_condition(True)
