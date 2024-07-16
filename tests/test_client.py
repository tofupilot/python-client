import pytest
import os
from datetime import timedelta
from tofupilot.client import TofuPilotClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def mock_post(mocker):
    return mocker.patch('tofupilot.client.requests.post')

def test_create_run(mock_post, mocker):
    # Mocking the response of the POST request
    mock_response = mocker.Mock()
    expected_response_json = {
        'url': 'https://www.tofupilot.com/runs/12345',
        'id': '12345'
    }
    mock_response.json.return_value = expected_response_json
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    api_key = os.getenv("TOFUPILOT_API_KEY")
    client = TofuPilotClient(api_key=api_key)

    response = client.create_run(
        procedure_id="FVT1",
        unit_under_test={
            "part_number": "PCB01",
            "serial_number": "00102"
        },
        run_passed=True,
        duration=timedelta(hours=1, minutes=32, seconds=18)
    )

    assert response['success']
    assert response['status_code'] == 200
    assert 'url' in response['message']
    assert response['message']['url'] == 'https://www.tofupilot.com/runs/12345'

def test_create_run_with_attachments(mocker, mock_post):
    # Mocking the response of the POST request
    mock_response = mocker.Mock()
    expected_response_json = {
        'url': 'https://www.tofupilot.com/runs/12345',
        'id': '12345'
    }
    mock_response.json.return_value = expected_response_json
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    # Mocking the upload and notification methods
    mocker.patch('tofupilot.utils.initialize_upload', return_value=('http://upload.url', 'upload_id'))
    mocker.patch('tofupilot.utils.upload_file', return_value=True)
    mocker.patch('tofupilot.utils.notify_server', return_value=True)

    api_key = os.getenv("TOFUPILOT_API_KEY")
    client = TofuPilotClient(api_key=api_key)

    response = client.create_run(
        procedure_id="FVT1",
        unit_under_test={
            "part_number": "PCB01",
            "serial_number": "00102"
        },
        run_passed=True,
        duration=timedelta(hours=1, minutes=32, seconds=18),
        attachments=["/Users/felix/Documents/Github/python-client/requirements.txt"]
    )

    assert response['success']
    assert response['status_code'] == 200
    assert 'url' in response['message']
    assert response['message']['url'] == 'https://www.tofupilot.com/runs/12345'
