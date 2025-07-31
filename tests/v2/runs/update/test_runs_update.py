"""Test run update operations."""

from datetime import datetime, timezone, timedelta
import requests
import tofupilot
from ...utils import assert_station_access_limited


def upload_to_presigned_url(presigned_url: str, content: bytes, content_type: str = "text/plain") -> None:
    """Helper function to upload content to a presigned URL."""
    response = requests.put(
        presigned_url,
        data=content,
        headers={"Content-Type": content_type}
    )
    assert response.status_code == 200, f"Upload failed with status {response.status_code}"


def download_from_url(download_url: str) -> bytes:
    """Helper function to download content from a URL."""
    response = requests.get(download_url)
    assert response.status_code == 200, f"Download failed with status {response.status_code}"
    return response.content


class TestRunsUpdate:
    
    def test_update_run_with_attachments(self, client: tofupilot.v2.TofuPilot, procedure_id: str, auth_type: str):
        """Test updating a run with attachments."""
        # First create a run with a proper serial number and part number
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        now = datetime.now(timezone.utc)
        create_result = client.runs.create(
            serial_number=f"ATTACHMENT-SIMPLE-{timestamp}",
            part_number=f"ATTACHMENT-PART-{timestamp}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=5),
            ended_at=now
        )
        run_id = create_result.id
        
        if auth_type == "station":
            # Stations have limited access to update runs
            with assert_station_access_limited("update run with attachments"):
                result = client.runs.update(
                    id=run_id,
                    attachments=["fake-attachment-id-1", "fake-attachment-id-2"]
                )
            return
        
        # Initialize two attachments
        attachment1 = client.attachments.initialize(name="test_file1.txt")
        attachment2 = client.attachments.initialize(name="test_file2.txt")
        
        # Upload content to presigned URLs
        test_content1 = b"Test file content 1"
        test_content2 = b"Test file content 2"
        
        # Upload to presigned URLs using helper function
        upload_to_presigned_url(attachment1.upload_url, test_content1)
        upload_to_presigned_url(attachment2.upload_url, test_content2)
        
        # Update run with attachments
        result = client.runs.update(
            id=run_id,
            attachments=[attachment1.id, attachment2.id]
        )
        
        assert hasattr(result, 'id')
        assert result.id == run_id
    
    def test_full_attachment_lifecycle(self, client: tofupilot.v2.TofuPilot, procedure_id: str, auth_type: str):
        """Test complete attachment lifecycle: create run, upload attachments, update run, and verify metadata."""
        # Step 1: Create a run
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        now = datetime.now(timezone.utc)
        create_result = client.runs.create(
            serial_number=f"ATTACHMENT-TESTING-{timestamp}",
            part_number=f"ATTACHMENT-TEST-PART-{timestamp}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=5),
            ended_at=now
        )
        run_id = create_result.id
        
        if auth_type == "station":
            # Stations have limited access to update runs with attachments
            with assert_station_access_limited("update run in full attachment lifecycle"):
                update_result = client.runs.update(
                    id=run_id,
                    attachments=["fake-attachment-id-1", "fake-attachment-id-2"]
                )
            return
        
        # Step 2: Initialize attachments
        attachment1 = client.attachments.initialize(name="lifecycle_test1.txt")
        attachment2 = client.attachments.initialize(name="lifecycle_test2.txt")
        
        # Step 3: Upload content to presigned URLs
        test_content1 = b"This is test content for file 1 in lifecycle test"
        test_content2 = b"This is test content for file 2 in lifecycle test"
        
        upload_to_presigned_url(attachment1.upload_url, test_content1, "text/plain")
        upload_to_presigned_url(attachment2.upload_url, test_content2, "text/plain")
        
        # Step 4: Update run with attachments
        update_result = client.runs.update(
            id=run_id,
            attachments=[attachment1.id, attachment2.id]
        )
        
        assert hasattr(update_result, 'id')
        assert update_result.id == run_id
        
        # Step 5: Get the run with attachments
        run_with_attachments = client.runs.get(id=run_id)
        
        # Verify attachments are present
        assert hasattr(run_with_attachments, 'attachments')
        assert run_with_attachments.attachments is not None
        assert len(run_with_attachments.attachments) == 2
        
        # Step 6: Verify attachment metadata
        # Print attachment structure to see what fields are available
        for att in run_with_attachments.attachments:
            print(f"\nAttachment: {att.name}")
            print(f"  ID: {att.id}")
            print(f"  Size: {att.size}")
            print(f"  Content Type: {att.content_type}")
            print(f"  Is Report: {att.is_report}")
            # Check for download_url attribute
            if hasattr(att, 'download_url'):
                print(f"  Download URL: {att.download_url[:50]}..." if att.download_url else "None")
            else:
                print("  Download URL: Not available in SDK (needs regeneration)")
            # Check if there are any other attributes
            print(f"  All attributes: {[attr for attr in dir(att) if not attr.startswith('_')]}")
        
        attachment_names = [att.name for att in run_with_attachments.attachments]
        attachment_ids = [att.id for att in run_with_attachments.attachments]
        
        # Verify names match
        assert "lifecycle_test1.txt" in attachment_names
        assert "lifecycle_test2.txt" in attachment_names
        
        # Verify IDs match
        assert attachment1.id in attachment_ids
        assert attachment2.id in attachment_ids
        
        # Verify attachment attributes
        for attachment in run_with_attachments.attachments:
            assert hasattr(attachment, 'id')
            assert hasattr(attachment, 'name')
            assert hasattr(attachment, 'size')
            assert hasattr(attachment, 'content_type')
            assert hasattr(attachment, 'is_report')
            
            # Verify is_report is False for these test files
            assert attachment.is_report is False
    
    def test_attachment_download_and_verify_content(self, client: tofupilot.v2.TofuPilot, procedure_id: str, auth_type: str):
        """Test complete attachment workflow with download and content verification."""
        # Step 1: Create a run
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        now = datetime.now(timezone.utc)
        create_result = client.runs.create(
            serial_number=f"ATTACHMENT-DOWNLOAD-TEST-{timestamp}",
            part_number=f"DOWNLOAD-TEST-PART-{timestamp}",
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=5),
            ended_at=now
        )
        run_id = create_result.id
        
        if auth_type == "station":
            # Stations have limited access to update runs with attachments
            with assert_station_access_limited("update run for download verification"):
                update_result = client.runs.update(
                    id=run_id,
                    attachments=["fake-text-attachment", "fake-json-attachment"]
                )
            return
        
        # Step 2: Initialize attachments with different content types
        attachment_text = client.attachments.initialize(name="test_document.txt")
        attachment_json = client.attachments.initialize(name="test_data.json")
        
        # Step 3: Prepare test content
        text_content = b"This is a test document\nWith multiple lines\nFor download verification"
        json_content = b'{"test": true, "data": [1, 2, 3], "message": "Download test"}'
        
        # Step 4: Upload content to presigned URLs
        upload_to_presigned_url(attachment_text.upload_url, text_content, "text/plain")
        upload_to_presigned_url(attachment_json.upload_url, json_content, "application/json")
        
        # Step 5: Update run with attachments
        update_result = client.runs.update(
            id=run_id,
            attachments=[attachment_text.id, attachment_json.id]
        )
        
        assert update_result.id == run_id
        
        # Step 6: Get the run with attachments (includes download URLs)
        run_with_attachments = client.runs.get(id=run_id)
        
        # Verify attachments are present
        assert hasattr(run_with_attachments, 'attachments')
        assert run_with_attachments.attachments is not None
        assert len(run_with_attachments.attachments) == 2
        
        # Step 7: Download and verify content for each attachment
        for attachment in run_with_attachments.attachments:
            # Verify download_url is present
            assert hasattr(attachment, 'download_url'), f"Attachment {attachment.name} missing download_url"
            assert attachment.download_url is not None, f"Attachment {attachment.name} has null download_url"
            
            # Type guard for Pylance - we already verified it's not None
            if not attachment.download_url:
                continue
            
            # Download the content
            downloaded_content = download_from_url(attachment.download_url)
            
            # Verify content based on attachment name
            if attachment.name == "test_document.txt":
                assert downloaded_content == text_content, "Text file content mismatch"
                # Note: content_type and size might not be updated after S3 upload
                # The important part is that we can download the correct content
                print(f"\nDownloaded text file: {len(downloaded_content)} bytes")
                print(f"Expected: {len(text_content)} bytes")
                print(f"Content matches: {downloaded_content == text_content}")
            elif attachment.name == "test_data.json":
                assert downloaded_content == json_content, "JSON file content mismatch"
                # Note: content_type and size might not be updated after S3 upload
                # The important part is that we can download the correct content
                print(f"\nDownloaded JSON file: {len(downloaded_content)} bytes")
                print(f"Expected: {len(json_content)} bytes")
                print(f"Content matches: {downloaded_content == json_content}")
            
            # Verify common attributes
            assert attachment.is_report is False
            assert attachment.id in [attachment_text.id, attachment_json.id]
        
        print(f"\nSuccessfully verified download and content for {len(run_with_attachments.attachments)} attachments")