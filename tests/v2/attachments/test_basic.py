"""Test basic attachment operations."""

from tofupilot.v2 import TofuPilot
from tofupilot.v2.models import AttachmentInitializeResponse

from trycast import checkcast


class TestAttachments:
    
    def test_initialize_upload(self, client: TofuPilot):
        """Test initializing file upload."""
        result = client.attachments.initialize(
            name="test_file.txt"
        )

        assert checkcast(AttachmentInitializeResponse, result)
    
    def test_initialize_upload_with_content_type(self, client: TofuPilot):
        """Test initializing file upload with content type."""
        result = client.attachments.initialize(
            name="test_image.png"
        )
        
        assert checkcast(AttachmentInitializeResponse, result)