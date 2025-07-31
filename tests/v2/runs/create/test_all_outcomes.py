"""Test all outcome types in runs.create()."""

import uuid  
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success, assert_station_access_limited


class TestRunOutcomes:
    """Test that all outcome types are properly supported."""
    
    def test_all_outcome_types(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test creating runs with all valid outcome types.
        
        The RunOutcome enum in the database schema supports:
        - PASS
        - FAIL  
        - ERROR
        - TIMEOUT
        - ABORTED
        
        This test verifies that all outcomes are properly preserved when creating runs.
        Station API keys might have access control restrictions based on procedure linking.
        """
        # Generate unique identifiers for this test to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        base_time = datetime.now(timezone.utc)
        
        # List of all outcomes to test
        outcomes_to_test = ["PASS", "FAIL", "ERROR", "TIMEOUT", "ABORTED"]
        
        for outcome in outcomes_to_test:
            # Both users and stations (if linked) should be able to create runs
            # If station is not linked to procedure, this will fail with appropriate error
            run = client.runs.create(
                outcome=outcome,
                procedure_id=procedure_id,
                serial_number=f"OUTCOME-TEST-{outcome}-{unique_id}",
                part_number=f"PCB-{outcome}-{unique_id}",
                started_at=base_time,
                ended_at=base_time
            )
            assert_create_run_success(run)
            
            # Verify the outcome was preserved
            retrieved = client.runs.get(id=run.id)
            assert retrieved.outcome == outcome, f"Expected outcome {outcome}, got {retrieved.outcome}"
            
            print(f"✓ {auth_type} API key successfully created run with outcome: {outcome}")
