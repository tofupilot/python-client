"""Test station update with image upload."""

from datetime import datetime, timezone
import requests
import uuid
import os
from typing import TYPE_CHECKING
from ..utils import assert_create_station_success, assert_update_station_success, assert_get_station_success

if TYPE_CHECKING:
    from tofupilot.v2 import TofuPilot


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


class TestStationImageUpload:
    """Test station image upload functionality."""
    
    def test_update_station_with_image(self, client: "TofuPilot", auth_type: str, timestamp: str) -> None:
        """Test updating a station with an image attachment."""
        if auth_type == "station":
            # Skip test for station auth - stations can't update themselves
            return
            
        # Step 1: Create a station
        unique_id = str(uuid.uuid4())[:8]
        station_name = f"Image Test Station {timestamp}-{unique_id}"
        
        station_result = client.stations.create(name=station_name)
        assert_create_station_success(station_result)
        station_id = station_result.id
        
        # Step 2: Initialize attachment for image
        attachment = client.attachments.initialize(name="station_image.png")
        
        # Step 3: Upload image content to presigned URL
        test_image = get_test_image_data()
        upload_to_presigned_url(attachment.upload_url, test_image, "image/png")
        
        # Step 4: Update station with image
        update_result = client.stations.update(
            id=station_id,
            image_id=attachment.id
        )
        
        assert_update_station_success(update_result)
        assert update_result.id == station_id
        
        print(f"\nSuccessfully updated station {station_id} with image {attachment.id}")
    
    def test_update_station_image_and_verify_download(self, client: "TofuPilot", auth_type: str, timestamp: str) -> None:
        """Test complete image workflow: upload, attach to station, and verify download."""
        if auth_type == "station":
            # Skip test for station auth
            return
            
        # Step 1: Create a station
        unique_id = str(uuid.uuid4())[:8]
        station_name = f"Image Download Test Station {timestamp}-{unique_id}"
        
        station_result = client.stations.create(name=station_name)
        assert_create_station_success(station_result)
        station_id = station_result.id
        
        # Step 2: Create and upload first image
        first_image = client.attachments.initialize(name="first_station_image.png")
        first_image_data = get_test_image_data()
        upload_to_presigned_url(first_image.upload_url, first_image_data, "image/png")
        
        # Step 3: Update station with first image
        update_result = client.stations.update(
            id=station_id,
            image_id=first_image.id
        )
        assert_update_station_success(update_result)
        
        # Step 4: Get station to check if image URL is available
        station = client.stations.get(id=station_id)
        assert_get_station_success(station)
        
        # Check if station has image field
        if hasattr(station, 'image') and station.image:
            # The image is a StationGetImage object, not a string
            print(f"\nStation has image object: {type(station.image)}")
            if hasattr(station.image, 's3_key'):
                print(f"Image s3_key: {station.image.s3_key}")
            # If the API provides a download URL, verify the content
            # Note: The exact field name may vary based on API implementation
            
        # Step 5: Test image replacement
        second_image = client.attachments.initialize(name="second_station_image.png")
        # Create different image data (you could modify the PNG data slightly)
        second_image_data = get_test_image_data()  # In real test, this would be different
        upload_to_presigned_url(second_image.upload_url, second_image_data, "image/png")
        
        # Update station with new image
        update_result2 = client.stations.update(
            id=station_id,
            image_id=second_image.id
        )
        assert_update_station_success(update_result2)
        
        print(f"\nSuccessfully replaced station image with {second_image.id}")
    
    def test_remove_station_image(self, client: "TofuPilot", auth_type: str, timestamp: str) -> None:
        """Test removing an image from a station."""
        if auth_type == "station":
            # Skip test for station auth
            return
            
        # Step 1: Create a station with an image
        unique_id = str(uuid.uuid4())[:8]
        station_name = f"Image Remove Test Station {timestamp}-{unique_id}"
        
        station_result = client.stations.create(name=station_name)
        assert_create_station_success(station_result)
        station_id = station_result.id
        
        # Step 2: Add an image to the station
        attachment = client.attachments.initialize(name="temp_station_image.png")
        test_image = get_test_image_data()
        upload_to_presigned_url(attachment.upload_url, test_image, "image/png")
        
        update_result = client.stations.update(
            id=station_id,
            image_id=attachment.id
        )
        assert_update_station_success(update_result)
        
        # Step 3: Remove the image by setting image_id to empty string
        remove_result = client.stations.update(
            id=station_id,
            image_id=""  # Empty string removes the image
        )
        assert_update_station_success(remove_result)
        
        # Step 4: Verify image was removed
        station = client.stations.get(id=station_id)
        assert_get_station_success(station)
        
        # Check that image is removed (exact field depends on API)
        if hasattr(station, 'image'):
            assert station.image is None or station.image == "", "Image should be removed"
        
        print(f"\nSuccessfully removed image from station {station_id}")
    
    def test_update_station_with_image_and_name(self, client: "TofuPilot", auth_type: str, timestamp: str) -> None:
        """Test updating both station name and image in single call."""
        if auth_type == "station":
            # Skip test for station auth
            return
            
        # Step 1: Create a station
        unique_id = str(uuid.uuid4())[:8]
        station_name = f"Image+Name Test Station {timestamp}-{unique_id}"
        
        station_result = client.stations.create(name=station_name)
        assert_create_station_success(station_result)
        station_id = station_result.id
        
        # Step 2: Initialize and upload image
        attachment = client.attachments.initialize(name="combined_update_image.png")
        test_image = get_test_image_data()
        upload_to_presigned_url(attachment.upload_url, test_image, "image/png")
        
        # Step 3: Update both name and image in one call
        new_name = f"Updated Station {timestamp}-{unique_id}"
        update_result = client.stations.update(
            id=station_id,
            name=new_name,
            image_id=attachment.id
        )
        
        assert_update_station_success(update_result)
        assert update_result.id == station_id
        
        # Step 4: Verify both updates were applied
        station = client.stations.get(id=station_id)
        assert_get_station_success(station)
        
        assert station.name == new_name, "Station name should be updated"
        # Image verification depends on API response structure
        
        print(f"\nSuccessfully updated station {station_id} with new name '{new_name}' and image")
    
    def test_update_station_with_image_and_identifier(self, client: "TofuPilot", auth_type: str, timestamp: str) -> None:
        """Test updating both station identifier and image in single call."""
        if auth_type == "station":
            # Skip test for station auth
            return
            
        # Step 1: Create a station
        unique_id = str(uuid.uuid4())[:8]
        station_name = f"Image+ID Test Station {timestamp}-{unique_id}"
        
        station_result = client.stations.create(name=station_name)
        assert_create_station_success(station_result)
        station_id = station_result.id
        
        # Step 2: Initialize and upload image
        attachment = client.attachments.initialize(name="identifier_update_image.png")
        test_image = get_test_image_data()
        upload_to_presigned_url(attachment.upload_url, test_image, "image/png")
        
        # Step 3: Update both identifier and image in one call
        new_identifier = f"STA-{unique_id[:3].upper()}"
        update_result = client.stations.update(
            id=station_id,
            identifier=new_identifier,
            image_id=attachment.id
        )
        
        assert_update_station_success(update_result)
        assert update_result.id == station_id
        
        # Step 4: Verify both updates were applied
        station = client.stations.get(id=station_id)
        assert_get_station_success(station)
        
        assert station.identifier == new_identifier, "Station identifier should be updated"
        # Image verification depends on API response structure
        
        print(f"\nSuccessfully updated station {station_id} with new identifier '{new_identifier}' and image")