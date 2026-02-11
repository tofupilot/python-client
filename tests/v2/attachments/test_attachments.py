"""Test attachment initialization validation."""

import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorBADREQUEST


class TestAttachmentInitialize:
    """Test attachment initialization validation."""

    def test_initialize_with_empty_name(self, client: TofuPilot) -> None:
        """Test that initializing an attachment with empty name fails."""
        with pytest.raises(ErrorBADREQUEST) as exc_info:
            client.attachments.initialize(name="")
        assert exc_info.value.data.issues and "name" in exc_info.value.data.issues[0].message.lower()

    def test_initialize_with_very_long_name(self, client: TofuPilot) -> None:
        """Test that initializing an attachment with very long name fails."""
        long_name = "a" * 1001 + ".txt"
        with pytest.raises(ErrorBADREQUEST) as exc_info:
            client.attachments.initialize(name=long_name)
        assert exc_info.value.data.issues and ("name" in exc_info.value.data.issues[0].message.lower() or "length" in exc_info.value.data.issues[0].message.lower())
