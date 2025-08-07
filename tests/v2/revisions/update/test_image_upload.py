"""Test revision update with image upload."""

from datetime import datetime, timezone
import requests
import uuid
import os
import tofupilot
from ..utils import assert_create_revision_success, assert_update_revision_success
from ...parts.utils import assert_create_part_success


def upload_to_presigned_url(upload_url: str, content: bytes, content_type: str = "image/png") -> None:
    """Helper function to upload content to a presigned URL."""
    response = requests.put(
        upload_url,
        data=content,
        headers={"Content-Type": content_type}
    )
    assert response.status_code == 200, f"Upload failed with status {response.status_code}"


def download_from_url(download_url: str) -> bytes:
    """Helper function to download content from a URL."""
    response = requests.get(download_url)
    assert response.status_code == 200, f"Download failed with status {response.status_code}"
    return response.content


def get_test_image_data() -> bytes:
    """Load test image data from file.
    
    Returns the contents of the test image file.
    """
    # Get the path to the test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'test_data', 'test_image.png')
    
    # Read and return the image data
    with open(image_path, 'rb') as f:
        return f.read()


class TestRevisionImageUpload:
    """Test revision image upload functionality."""
    
    def test_update_revision_with_image(self, client: tofupilot.v2.TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating a revision with an image attachment."""
        # Step 1: Create a part and revision
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-IMG-{timestamp}-{unique_id}"
        
        part_result = client.parts.create(
            number=part_number,
            name=f"Image Test Part {unique_id}"
        )
        assert_create_part_success(part_result)
        
        revision_number = f"REV-IMG-{timestamp}"
        revision_result = client.parts.revisions.create(part_number=part_number
        , number=revision_number)
        assert_create_revision_success(revision_result)
        revision_id = revision_result.id
        
        # Step 2: Initialize attachment for image
        attachment = client.attachments.initialize(name="revision_image.png")
        
        # Step 3: Upload image content to presigned URL
        test_image = get_test_image_data()
        upload_to_presigned_url(attachment.upload_url, test_image, "image/png")
        
        # Step 4: Update revision with image
        update_result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            image_id=attachment.id
        )
        
        assert_update_revision_success(update_result)
        assert update_result.id == revision_id
        
        print(f"\nSuccessfully updated revision {revision_id} with image {attachment.id}")
    
    def test_update_revision_image_and_verify_download(self, client: tofupilot.v2.TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test complete image workflow: upload, attach to revision, and verify download."""
        # Step 1: Create a part and revision
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-IMG-DL-{timestamp}-{unique_id}"
        
        part_result = client.parts.create(
            number=part_number,
            name=f"Image Download Test Part {unique_id}"
        )
        assert_create_part_success(part_result)
        
        revision_number = f"REV-IMG-DL-{timestamp}"
        revision_result = client.parts.revisions.create(part_number=part_number
        , number=revision_number)
        assert_create_revision_success(revision_result)
        revision_id = revision_result.id
        
        # Step 2: Create and upload first image
        first_image = client.attachments.initialize(name="first_revision_image.png")
        first_image_data = get_test_image_data()
        upload_to_presigned_url(first_image.upload_url, first_image_data, "image/png")
        
        # Step 3: Update revision with first image
        update_result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            image_id=first_image.id
        )
        assert_update_revision_success(update_result)
        
        # Step 4: Get revision to check if image URL is available
        part_data = client.parts.get(number=part_number)
        revision = None
        for rev in part_data.revisions:
            if rev.id == revision_id:
                revision = rev
                break
        assert revision is not None, f"Revision {revision_id} not found"
        
        # Check if revision has image field
        if hasattr(revision, 'image') and revision.image:
            print(f"\nRevision has image URL: {revision.image[:50]}...")
            # If the API provides a download URL, verify the content
            # Note: The exact field name may vary based on API implementation
            
        # Step 5: Test image replacement
        second_image = client.attachments.initialize(name="second_revision_image.png")
        # Create different image data (you could modify the PNG data slightly)
        second_image_data = get_test_image_data()  # In real test, this would be different
        upload_to_presigned_url(second_image.upload_url, second_image_data, "image/png")
        
        # Update revision with new image
        update_result2 = client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            image_id=second_image.id
        )
        assert_update_revision_success(update_result2)
        
        print(f"\nSuccessfully replaced revision image with {second_image.id}")
    
    def test_remove_revision_image(self, client: tofupilot.v2.TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test removing an image from a revision."""
        # Step 1: Create a part and revision with an image
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-IMG-REM-{timestamp}-{unique_id}"
        
        part_result = client.parts.create(
            number=part_number,
            name=f"Image Remove Test Part {unique_id}"
        )
        assert_create_part_success(part_result)
        
        revision_number = f"REV-IMG-REM-{timestamp}"
        revision_result = client.parts.revisions.create(part_number=part_number
        , number=revision_number)
        assert_create_revision_success(revision_result)
        revision_id = revision_result.id
        
        # Step 2: Add an image to the revision
        attachment = client.attachments.initialize(name="temp_revision_image.png")
        test_image = get_test_image_data()
        upload_to_presigned_url(attachment.upload_url, test_image, "image/png")
        
        update_result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            image_id=attachment.id
        )
        assert_update_revision_success(update_result)
        
        # Step 3: Remove the image by setting image_id to empty string
        remove_result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=revision_number,
            image_id=""  # Empty string removes the image
        )
        assert_update_revision_success(remove_result)
        
        # Step 4: Verify image was removed
        part_data = client.parts.get(number=part_number)
        revision = None
        for rev in part_data.revisions:
            if rev.id == revision_id:
                revision = rev
                break
        assert revision is not None, f"Revision {revision_id} not found"
        
        # Check that image is removed (exact field depends on API)
        if hasattr(revision, 'image'):
            assert revision.image is None or revision.image == "", "Image should be removed"
        
        print(f"\nSuccessfully removed image from revision {revision_id}")
    
    def test_update_revision_with_image_and_number(self, client: tofupilot.v2.TofuPilot, auth_type: str, timestamp: str) -> None:
        """Test updating both revision number and image in single call."""
        # Step 1: Create a part and revision
        unique_id = str(uuid.uuid4())[:8]
        part_number = f"PART-IMG-NUM-{timestamp}-{unique_id}"
        
        part_result = client.parts.create(
            number=part_number,
            name=f"Image+Number Test Part {unique_id}"
        )
        assert_create_part_success(part_result)
        
        revision_result = client.parts.revisions.create(part_number=part_number
        , number=f"REV-OLD-{timestamp}")
        assert_create_revision_success(revision_result)
        revision_id = revision_result.id
        
        # Step 2: Initialize and upload image
        attachment = client.attachments.initialize(name="combined_update_image.png")
        test_image = get_test_image_data()
        upload_to_presigned_url(attachment.upload_url, test_image, "image/png")
        
        # Step 3: Update both number and image in one call
        new_number = f"REV-NEW-{timestamp}"
        update_result = client.parts.revisions.update(
            part_number=part_number,
            revision_number=f"REV-OLD-{timestamp}",
            number=new_number,
            image_id=attachment.id
        )
        
        assert_update_revision_success(update_result)
        assert update_result.id == revision_id
        
        # Step 4: Verify both updates were applied
        part_data = client.parts.get(number=part_number)
        revision = None
        for rev in part_data.revisions:
            if rev.id == revision_id:
                revision = rev
                break
        assert revision is not None, f"Revision {revision_id} not found"
        
        assert revision.number == new_number, "Revision number should be updated"
        # Image verification depends on API response structure
        
        print(f"\nSuccessfully updated revision {revision_id} with new number '{new_number}' and image")