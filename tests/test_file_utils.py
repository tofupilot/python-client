import pytest
from unittest.mock import Mock, patch, mock_open
from datetime import timedelta
from typing import List

# Import the functions to be tested
from src.utils import (
    validate_attachments, 
    initialize_upload, 
    upload_file, 
    notify_server, 
    handle_attachments, 
    parse_error_message, 
    timedelta_to_iso8601, 
    allowed_formats
)

def test_validate_attachments():
    logger = Mock()
    attachments = ['file1.txt', 'file2.csv']
    max_attachments = 2
    max_file_size = 1024
    allowed_file_formats = allowed_formats

    with patch('os.path.getsize', return_value=500):
        validate_attachments(logger, attachments, max_attachments, max_file_size, allowed_file_formats)

    logger.error.assert_not_called()

    with pytest.raises(RuntimeError):
        validate_attachments(logger, ['file1.txt', 'file2.csv', 'file3.png'], 2, 1024, allowed_file_formats)

    logger.error.assert_called_once_with("Number of attachments exceeds the maximum allowed limit of 2")

def test_initialize_upload(requests_mock):
    headers = {'Authorization': 'Bearer token'}
    base_url = 'http://example.com'
    file_path = 'file.txt'
    mock_response = {'uploadUrl': 'http://example.com/upload', 'id': '12345'}
    requests_mock.post(f'{base_url}/uploads/initialize', json=mock_response)

    upload_url, upload_id = initialize_upload(headers, base_url, file_path)

    assert upload_url == 'http://example.com/upload'
    assert upload_id == '12345'

def test_upload_file(requests_mock):
    upload_url = 'http://example.com/upload'
    file_path = 'file.txt'
    requests_mock.put(upload_url, status_code=200)

    with patch('builtins.open', mock_open(read_data='data')):
        result = upload_file(upload_url, file_path)

    assert result is True

def test_notify_server(requests_mock):
    headers = {'Authorization': 'Bearer token'}
    base_url = 'http://example.com'
    upload_id = '12345'
    run_id = '67890'
    requests_mock.post(f'{base_url}/uploads/sync', status_code=200)

    result = notify_server(headers, base_url, upload_id, run_id)

    assert result is True

def test_handle_attachments():
    logger = Mock()
    headers = {'Authorization': 'Bearer token'}
    base_url = 'http://example.com'
    attachments = ['file1.txt']
    run_id = '67890'

    with patch('src.utils.initialize_upload', return_value=('http://example.com/upload', '12345')):
        with patch('src.utils.upload_file', return_value=True):
            with patch('src.utils.notify_server', return_value=True):
                handle_attachments(logger, headers, base_url, attachments, run_id)

    logger.info.assert_any_call(f"Uploading file1.txt...")

def test_parse_error_message():
    response = Mock()
    response.json.return_value = {"error": {"message": "Error occurred"}}

    message = parse_error_message(response)

    assert message == "Error occurred"

    response.json.side_effect = ValueError
    response.text = 'Error text'

    message = parse_error_message(response)

    assert message == "HTTP error occurred: Error text"

def test_timedelta_to_iso8601():
    td = timedelta(days=1, hours=2, minutes=3, seconds=4, microseconds=500000)
    iso_duration = timedelta_to_iso8601(td)

    assert iso_duration == "P1DT2H3M4.500000S"