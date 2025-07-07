import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

@pytest.fixture(scope="class")
def tofupilot_server_url():
    # Get URL from environment
    url = os.environ.get("TOFUPILOT_URL")
    
    if not url:
        pytest.fail(
            "TOFUPILOT_URL environment variable not set. "
            "Set it to run tests against local server:\n"
            "export TOFUPILOT_URL='the-url-you-want-to-test'"
        )
    return url

@pytest.fixture(scope="class")
def station_api_key():
    # Get API key from environment
    api_key = os.environ.get("TOFUPILOT_API_KEY_STATION")
    
    if not api_key:
        pytest.fail(
            "TOFUPILOT_API_KEY_STATION environment variable not set. "
            "Set it to run tests against local server:\n"
            "export TOFUPILOT_API_KEY_STATION='your-local-api-key'"
        )
    return api_key

@pytest.fixture(scope="class")
def user_api_key():
    # Get API key from environment
    api_key = os.environ.get("TOFUPILOT_API_KEY_USER")
    
    if not api_key:
        pytest.fail(
            "TOFUPILOT_API_KEY_USER environment variable not set. "
            "Set it to run tests against local server:\n"
            "export TOFUPILOT_API_KEY_USER='your-local-api-key'"
        )
    return api_key

@pytest.fixture(scope="class", params=["user", "station"])
def api_key(request, user_api_key, station_api_key):
    """Fixture that provides both user and station API keys for testing."""
    if request.param == "user":
        return user_api_key
    elif request.param == "station":
        return station_api_key
    else:
        raise ValueError(f"Unknown api_key type: {request.param}")

@pytest.fixture(scope="class")
def procedure_identifier():
    """Update this with the procedure identifier you get in local"""
    procedure_identifier = os.environ.get("TOFUPILOT_PROCEDURE_IDENTIFIER")
    
    if not procedure_identifier:
        pytest.fail(
            "TOFUPILOT_PROCEDURE_IDENTIFIER environment variable not set. "
            "Set it to run tests against local server:\n"
            "export TOFUPILOT_PROCEDURE_IDENTIFIER='your-procedure-identifier'"
        )
    return procedure_identifier

@pytest.fixture(scope="class")
def procedure_id():
    """Update this with the procedure id you get in local (see url)"""
    procedure_id = os.environ.get("TOFUPILOT_PROCEDURE_ID")
    
    if not procedure_id:
        pytest.fail(
            "TOFUPILOT_PROCEDURE_ID environment variable not set. "
            "Set it to run tests against local server:\n"
            "export TOFUPILOT_PROCEDURE_ID='your-procedure-id'"
        )
    return procedure_id