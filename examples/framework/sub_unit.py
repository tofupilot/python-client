from tofupilot import conf

conf.set(
    procedure_id="FVT1",
    serial_number="PCBA01-0001",
    sub_units=[{"serial_number": "123"}],
)


def test_pass():
    assert True
