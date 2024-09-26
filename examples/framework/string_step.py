from tofupilot import conf, string_step

conf.set(procedure_id="FVT2", serial_number="PCBA01-0001", part_number="PCBA01")


def test_passing_step():
    assert True


@string_step
def test_string_limit(step):
    step.set_name("My string limit step").set_limit("1.2.A")

    step.measure("1.2.A")

    assert step()
