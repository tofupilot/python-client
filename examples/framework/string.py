from tofupilot import conf, string_step

conf.set(procedure_id="FVT1", serial_number="PCBA01-0001")


@string_step
def test_string_limit(step):
    step.set_name("My string limit step").set_limit("1.2.A")

    step.measure("1.2.A")

    assert step()
