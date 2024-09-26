from tofupilot import conf

conf.set(
    procedure_id="FVT1",
    serial_number="PCBA01-0001",
    attachments=[
        "data/temperature-map.png",  # Path to your local files
        "data/performance-report.pdf",
    ],
)


def test_pass():
    assert True
