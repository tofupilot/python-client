"""Test parts update validation rules."""

from datetime import datetime, timezone
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import APIError, ErrorBADREQUEST, ErrorCONFLICT, ErrorNOTFOUND
from ..utils import assert_create_part_success
from ...utils import assert_station_access_forbidden


class TestUpdatePartValidation:
    """Test parts update validation scenarios."""

    def test_update_nonexistent_part(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a part that doesn't exist."""
        if auth_type == "station":
            with assert_station_access_forbidden("update nonexistent part"):
                client.parts.update(number="NONEXISTENT-PART-12345", name="New Name")
            return

        with pytest.raises(ErrorNOTFOUND):
            client.parts.update(number="NONEXISTENT-PART-12345", name="New Name")

    def test_update_invalid_number_format(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating with empty number — resolves to a non-existent route or redirect."""
        with pytest.raises((ErrorNOTFOUND, APIError)):
            client.parts.update(number="", name="New Name")

    def test_update_duplicate_part_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating to a part number that already exists."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part to duplicate number"):
                client.parts.update(number="any", new_number="any2")
            return

        part1_number = f"PART1-{timestamp}"
        part2_number = f"PART2-{timestamp}"
        part1 = client.parts.create(number=part1_number)
        assert_create_part_success(part1)
        part2 = client.parts.create(number=part2_number)
        assert_create_part_success(part2)

        with pytest.raises(ErrorCONFLICT):
            client.parts.update(number=part2_number, new_number=part1_number)

    def test_update_empty_part_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part with empty number."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part with empty new number"):
                client.parts.update(number="any", new_number="")
            return

        part_number = f"PART-{timestamp}"
        client.parts.create(number=part_number)

        with pytest.raises((APIError, ErrorBADREQUEST)):
            client.parts.update(number=part_number, new_number="")

    def test_update_part_number_too_long(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part with number > 60 chars."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part with long number"):
                client.parts.update(number="any", new_number="X" * 61)
            return

        part_number = f"PART-{timestamp}"
        client.parts.create(number=part_number)

        with pytest.raises((APIError, ErrorBADREQUEST)):
            client.parts.update(number=part_number, new_number="X" * 61)

    def test_update_part_name_too_long(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part with name > 255 chars."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part with long name"):
                client.parts.update(number="any", name="Y" * 256)
            return

        part_number = f"PART-{timestamp}"
        client.parts.create(number=part_number)

        with pytest.raises((APIError, ErrorBADREQUEST)):
            client.parts.update(number=part_number, name="Y" * 256)

    def test_update_no_fields_provided(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part without providing any fields to update."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part with no fields"):
                client.parts.update(number="any")
            return

        part_number = f"PART-{timestamp}"
        client.parts.create(number=part_number)

        with pytest.raises((APIError, ErrorBADREQUEST)):
            client.parts.update(number=part_number)

    def test_update_case_insensitive_conflict(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test that part number uniqueness is case-insensitive on update."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part number case conflict"):
                client.parts.update(number="any", new_number="OTHER")
            return

        part1_number = f"part-lower-{timestamp}"
        client.parts.create(number=part1_number)
        part2_number = f"PART-UPPER-{timestamp}"
        client.parts.create(number=part2_number)

        with pytest.raises(ErrorCONFLICT):
            client.parts.update(number=part2_number, new_number=f"PART-LOWER-{timestamp}")

    def test_update_to_same_number(self, client: TofuPilot, auth_type: str, timestamp) -> None:
        """Test updating part to its current number (should succeed)."""
        if auth_type == "station":
            with assert_station_access_forbidden("update part same number"):
                client.parts.update(number="any", new_number="any", name="test")
            return

        part_number = f"PART-SAME-{timestamp}"
        client.parts.create(number=part_number, name="Original Name")

        result = client.parts.update(
            number=part_number,
            new_number=part_number,
            name="Updated Name"
        )
        assert result.number == part_number
        assert result.name == "Updated Name"
