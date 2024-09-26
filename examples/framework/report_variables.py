from tofupilot import conf

conf.set(
    procedure_id="FVT1",
    serial_number="PCBA01-0001",
    report_variables={"var": "42"},
)


def test_pass():
    assert True
