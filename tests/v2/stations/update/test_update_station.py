"""Test updating station details."""

from datetime import datetime, timezone
import uuid
import pytest
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ..utils import assert_create_station_success, assert_update_station_success


class TestUpdateStation:
    """Test updating station details."""
    
    def test_update_station_name(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a station's name."""
        if auth_type == "station":
            # Skip test for station auth
            return
        
        # Create a station
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        original_name = f"Original Station Name - {timestamp}"
        
        create_result = client.stations.create(name=original_name)
        assert_create_station_success(create_result)
        station_id = create_result.id
        
        # Update the name
        new_name = f"Updated Station Name - {timestamp}"
        update_result = client.stations.update(
            id=station_id,
            name=new_name
        )
        assert_update_station_success(update_result)
        
        # Verify the update
        get_result = client.stations.get(id=station_id)
        assert get_result.name == new_name
        # Identifier should remain unchanged
        assert get_result.identifier == update_result.identifier
    
    def test_update_station_identifier(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a station's identifier."""
        if auth_type == "station":
            # Skip test for station auth
            return
        
        # Create a station
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        station_name = f"Station for ID Update - {timestamp}"
        
        create_result = client.stations.create(name=station_name)
        assert_create_station_success(create_result)
        station_id = create_result.id
        
        # Generate a new unique identifier
        new_identifier = f"STA-{str(uuid.uuid4())[:3].upper()}"
        
        # Update the identifier
        update_result = client.stations.update(
            id=station_id,
            identifier=new_identifier
        )
        assert_update_station_success(update_result)
        assert update_result.identifier == new_identifier
        
        # Verify via get
        get_result = client.stations.get(id=station_id)
        assert get_result.identifier == new_identifier
        assert get_result.name == station_name  # Name unchanged
    
    def test_update_station_both_fields(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating both name and identifier simultaneously."""
        if auth_type == "station":
            # Skip test for station auth
            return
        
        # Create a station
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        create_result = client.stations.create(name=f"Initial Station - {timestamp}")
        station_id = create_result.id
        
        # Update both fields
        new_name = f"Fully Updated Station - {timestamp}"
        new_identifier = f"STA-{str(uuid.uuid4())[:3].upper()}"
        
        update_result = client.stations.update(
            id=station_id,
            name=new_name,
            identifier=new_identifier
        )
        assert_update_station_success(update_result)
        assert update_result.name == new_name
        assert update_result.identifier == new_identifier
    
    def test_update_station_nonexistent(self, client: TofuPilot, auth_type: str) -> None:
        """Test updating a station that doesn't exist."""
        if auth_type == "station":
            # Skip test for station auth
            return
        
        nonexistent_id = str(uuid.uuid4())
        
        with pytest.raises(ErrorNOTFOUND):
            client.stations.update(
                id=nonexistent_id,
                name="New Name"
            )
    
    
    def test_update_station_remove_image(self, client: TofuPilot, auth_type: str) -> None:
        """Test removing a station's image by passing empty string."""
        if auth_type == "station":
            # Skip test for station auth
            return
        
        # Create a station
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        create_result = client.stations.create(name=f"Station with Image - {timestamp}")
        station_id = create_result.id
        
        # Note: To fully test this, we would need to upload an image first
        # For now, just test that empty string is accepted
        update_result = client.stations.update(
            id=station_id,
            image_id=""  # Empty string to remove image
        )
        assert_update_station_success(update_result)
        
        # Verify image is None
        get_result = client.stations.get(id=station_id)
        assert get_result.image is None
    
    def test_update_station_partial_update(self, client: TofuPilot, auth_type: str) -> None:
        """Test that unspecified fields remain unchanged during update."""
        if auth_type == "station":
            # Skip test for station auth
            return
        
        # Create a station
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        original_name = f"Partial Update Test - {timestamp}"
        
        create_result = client.stations.create(name=original_name)
        station_id = create_result.id
        
        # Get original details
        original = client.stations.get(id=station_id)
        
        # Update only the name
        new_name = f"Partially Updated - {timestamp}"
        client.stations.update(id=station_id, name=new_name)
        
        # Verify only name changed
        updated = client.stations.get(id=station_id)
        assert updated.name == new_name
        assert updated.identifier == original.identifier  # Unchanged
        assert updated.image == original.image  # Unchanged