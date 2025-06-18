"""Integration tests for legacy steps functionality."""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

import pytest

from tofupilot import TofuPilotClient


def convert_datetime_to_ms(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert datetime objects in steps to milliseconds."""
    for step in steps:
        if "started_at" in step and isinstance(step["started_at"], datetime):
            step["started_at"] = int(step["started_at"].timestamp() * 1000)
    return steps


@pytest.mark.integration
def test_legacy_steps_required(client: TofuPilotClient):
    """Test required step parameters (name, step_passed, duration, started_at)."""
    serial_number = f"QA-{random.randint(100000, 999999)}"
    part_number = "PCB-001"
    
    base_time = datetime.now() - timedelta(minutes=5)
    base_time_ms = int(base_time.timestamp() * 1000)
    
    steps = [
        {
            "name": "Initialize System",
            "step_passed": True,
            "duration": 1000,  # milliseconds
            "started_at": base_time_ms
        },
        {
            "name": "Run Test",
            "step_passed": True,
            "duration": 2500,
            "started_at": base_time_ms + 1000
        },
        {
            "name": "Cleanup",
            "step_passed": True,
            "duration": 500,
            "started_at": base_time_ms + 3500
        }
    ]
    
    run_response = client.run_create(
        serial_number=serial_number,
        part_number=part_number,
        steps=steps,
        outcome="PASS"
    )
    
    assert run_response is not None


@pytest.mark.integration
def test_legacy_steps_optional(client: TofuPilotClient):
    """Test optional step parameters (measurement_value, units, limits)."""
    serial_number = f"QA-{random.randint(100000, 999999)}"
    part_number = "PCB-001"
    
    base_time = datetime.now() - timedelta(minutes=5)
    base_time_ms = int(base_time.timestamp() * 1000)
    
    steps = [
        {
            "name": "Voltage Measurement",
            "step_passed": True,
            "duration": 1500,
            "started_at": base_time_ms,
            "measurement_value": 5.1,
            "units": "V",
            "lower_limit": 4.5,
            "upper_limit": 5.5
        },
        {
            "name": "Current Measurement",
            "step_passed": True,
            "duration": 1200,
            "started_at": base_time_ms + 1500,
            "measurement_value": 0.8,
            "units": "A",
            "lower_limit": 0.5,
            "upper_limit": 1.0
        },
        {
            "name": "Temperature Check",
            "step_passed": False,  # Failed test
            "duration": 800,
            "started_at": base_time_ms + 2700,
            "measurement_value": 75.2,
            "units": "°C",
            "lower_limit": 20.0,
            "upper_limit": 70.0
        }
    ]
    
    run_response = client.run_create(
        serial_number=serial_number,
        part_number=part_number,
        steps=steps,
        outcome="FAIL"  # Overall fail due to temperature
    )
    
    assert run_response is not None


@pytest.mark.integration
def test_legacy_steps_advanced(client: TofuPilotClient):
    """Complex test with multiple steps and various measurement types."""
    serial_number = f"QA-{random.randint(100000, 999999)}"
    part_number = "PCB-001"
    
    base_time = datetime.now() - timedelta(minutes=10)
    
    steps = [
        # Initialization steps
        {
            "name": "Power On",
            "step_passed": True,
            "duration": 500,
            "started_at": base_time
        },
        {
            "name": "Self Test",
            "step_passed": True,
            "duration": 2000,
            "started_at": base_time + timedelta(seconds=0.5)
        },
        
        # Voltage tests
        {
            "name": "3.3V Rail Check",
            "step_passed": True,
            "duration": 1000,
            "started_at": base_time + timedelta(seconds=2.5),
            "measurement_value": 3.31,
            "units": "V",
            "lower_limit": 3.25,
            "upper_limit": 3.35
        },
        {
            "name": "5V Rail Check", 
            "step_passed": True,
            "duration": 1000,
            "started_at": base_time + timedelta(seconds=3.5),
            "measurement_value": 5.02,
            "units": "V",
            "lower_limit": 4.95,
            "upper_limit": 5.05
        },
        {
            "name": "12V Rail Check",
            "step_passed": True,
            "duration": 1000,
            "started_at": base_time + timedelta(seconds=4.5),
            "measurement_value": 11.98,
            "units": "V",
            "lower_limit": 11.88,
            "upper_limit": 12.12
        },
        
        # Current tests
        {
            "name": "Idle Current",
            "step_passed": True,
            "duration": 1500,
            "started_at": base_time + timedelta(seconds=5.5),
            "measurement_value": 0.15,
            "units": "A",
            "lower_limit": 0.1,
            "upper_limit": 0.2
        },
        {
            "name": "Load Current",
            "step_passed": True,
            "duration": 2000,
            "started_at": base_time + timedelta(seconds=7),
            "measurement_value": 1.85,
            "units": "A",
            "lower_limit": 1.5,
            "upper_limit": 2.0
        },
        
        # Frequency and timing tests
        {
            "name": "Clock Frequency",
            "step_passed": True,
            "duration": 3000,
            "started_at": base_time + timedelta(seconds=9),
            "measurement_value": 100000000,  # 100 MHz
            "units": "Hz",
            "lower_limit": 99900000,
            "upper_limit": 100100000
        },
        
        # Temperature and environmental
        {
            "name": "Operating Temperature",
            "step_passed": True,
            "duration": 1000,
            "started_at": base_time + timedelta(seconds=12),
            "measurement_value": 45.2,
            "units": "°C",
            "lower_limit": 0.0,
            "upper_limit": 85.0
        },
        
        # Final validation
        {
            "name": "System Integration Test",
            "step_passed": True,
            "duration": 5000,
            "started_at": base_time + timedelta(seconds=13),
            "measurement_value": 98.5,
            "units": "%",
            "lower_limit": 95.0,
            "upper_limit": 100.0
        },
        
        # Cleanup
        {
            "name": "Power Down",
            "step_passed": True,
            "duration": 500,
            "started_at": base_time + timedelta(seconds=18)
        }
    ]
    
    # Convert datetime objects to milliseconds
    steps = convert_datetime_to_ms(steps)
    
    run_response = client.run_create(
        serial_number=serial_number,
        part_number=part_number,
        steps=steps,
        outcome="PASS"
    )
    
    assert run_response is not None