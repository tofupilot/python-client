"""Test measurements list filtering, pagination, and sorting (public V2 endpoint)."""

from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, get_random_test_dates
from ....e2e_tag import uid


def _seed_run_with_measurements(client: TofuPilot, procedure_id: str, part_number: str, serial: str):
    started_at, ended_at = get_random_test_dates()
    result = client.runs.create(
        serial_number=serial,
        procedure_id=procedure_id,
        part_number=part_number,
        started_at=started_at,
        outcome="FAIL",
        ended_at=ended_at,
        phases=[
            {
                "name": "Power",
                "outcome": "FAIL",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {"name": "Voltage", "outcome": "FAIL", "measured_value": 3.9, "units": "V"},
                    {"name": "Enabled", "outcome": "PASS", "measured_value": True},
                ],
            },
            {
                "name": "Report",
                "outcome": "PASS",
                "started_at": started_at,
                "ended_at": ended_at,
                "measurements": [
                    {"name": "Serial", "outcome": "PASS", "measured_value": "OK"},
                ],
            },
        ],
    )
    assert_create_run_success(result)
    return result.id


class TestListMeasurements:
    """Test measurements list filtering, pagination, and sorting."""

    def test_list_returns_measurements_across_types(self, client: TofuPilot, procedure_id: str) -> None:
        """Measurements of mixed value types are returned for the run."""
        unique_id = uid()
        run_id = _seed_run_with_measurements(
            client, procedure_id, f"PART-M-{unique_id}", f"SN-M-{unique_id}"
        )

        result = client.measurements.list(procedure_id=procedure_id, ids=[run_id])
        assert len(result.data) == 3
        assert all(m.run_id == run_id for m in result.data)
        assert {m.measurement_type for m in result.data} == {"numeric", "boolean", "string"}

        voltage = next(m for m in result.data if m.measurement_name == "Voltage")
        assert voltage.value == 3.9
        assert voltage.units == "V"
        enabled = next(m for m in result.data if m.measurement_name == "Enabled")
        assert enabled.bool_value is True

    def test_measurement_outcomes_filter(self, client: TofuPilot, procedure_id: str) -> None:
        """The measurement_outcomes filter narrows to matching measurements."""
        unique_id = uid()
        run_id = _seed_run_with_measurements(
            client, procedure_id, f"PART-MO-{unique_id}", f"SN-MO-{unique_id}"
        )

        result = client.measurements.list(
            procedure_id=procedure_id, ids=[run_id], measurement_outcomes=["FAIL"]
        )
        assert len(result.data) == 1
        assert result.data[0].measurement_name == "Voltage"
        assert result.data[0].measurement_outcome == "FAIL"

    def test_single_pair_pin(self, client: TofuPilot, procedure_id: str) -> None:
        """phase_name + measurement_name pin to a single measurement."""
        unique_id = uid()
        run_id = _seed_run_with_measurements(
            client, procedure_id, f"PART-MP-{unique_id}", f"SN-MP-{unique_id}"
        )

        result = client.measurements.list(
            procedure_id=procedure_id,
            ids=[run_id],
            phase_name="Power",
            measurement_name="Voltage",
        )
        assert len(result.data) == 1
        assert result.data[0].measurement_name == "Voltage"
        assert result.data[0].phase_name == "Power"

    def test_limit_and_cursor_pagination(self, client: TofuPilot, procedure_id: str) -> None:
        """limit caps the page and next_cursor walks the result set."""
        unique_id = uid()
        run_id = _seed_run_with_measurements(
            client, procedure_id, f"PART-MPG-{unique_id}", f"SN-MPG-{unique_id}"
        )

        page1 = client.measurements.list(procedure_id=procedure_id, ids=[run_id], limit=2)
        assert len(page1.data) == 2
        assert page1.meta.has_more is True
        assert page1.meta.next_cursor is not None

        page2 = client.measurements.list(
            procedure_id=procedure_id, ids=[run_id], limit=2, cursor=page1.meta.next_cursor
        )
        assert len(page2.data) == 1
        assert page2.meta.has_more is False
        ids = {m.id for m in page1.data} | {m.id for m in page2.data}
        assert len(ids) == 3
