import json
from datetime import timedelta
from unittest.mock import MagicMock, patch, mock_open

import pytest
from tofupilot.utils import (
    validate_attachments,
    initialize_upload,
    upload_file,
    notify_server,
    parse_error_message,
    timedelta_to_iso,
    log_and_raise,
)


def test_validate_attachments():
    logger = MagicMock()
    attachments = ["file1.txt", "file2.jpg"]
    max_attachments = 2
    max_file_size = 5000
    allowed_file_formats = [".txt", ".jpg"]

    with patch("os.path.getsize", return_value=4000):
        validate_attachments(
            logger, attachments, max_attachments, max_file_size, allowed_file_formats
        )

    logger.info.assert_called_with("Validating attachments...")
    logger.error.assert_not_called()

    with pytest.raises(RuntimeError):
        with patch("os.path.getsize", return_value=6000):
            validate_attachments(
                logger,
                attachments,
                max_attachments,
                max_file_size,
                allowed_file_formats,
            )

    logger.error.assert_called_with(
        "File size exceeds the maximum allowed size of 5000 bytes: file1.txt"
    )


def test_initialize_upload():
    headers = {"Authorization": "Bearer token"}
    base_url = "http://example.com"
    file_path = "file.txt"
    response_data = {"uploadUrl": "http://example.com/upload", "id": "123"}

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = response_data

        upload_url, upload_id = initialize_upload(headers, base_url, file_path)

        assert upload_url == response_data["uploadUrl"]
        assert upload_id == response_data["id"]


def test_upload_file():
    upload_url = "http://example.com/upload"
    file_path = "file.txt"
    file_content = b"file content"

    with patch("builtins.open", mock_open(read_data=file_content)) as mock_file, patch(
        "requests.put"
    ) as mock_put, patch("mimetypes.guess_type", return_value=("text/plain", None)):
        mock_put.return_value.status_code = 200

        result = upload_file(upload_url, file_path)

        assert result is True
        mock_file.assert_called_once_with(file_path, "rb")
        mock_put.assert_called_with(
            upload_url,
            data=mock_file(),
            headers={"Content-Type": "text/plain"},
            timeout=10,
        )


def test_notify_server():
    headers = {"Authorization": "Bearer token"}
    base_url = "http://example.com"
    upload_id = "123"
    run_id = "456"

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        result = notify_server(headers, base_url, upload_id, run_id)

        assert result is True
        mock_post.assert_called_with(
            f"{base_url}/uploads/sync",
            data=json.dumps({"upload_id": upload_id, "run_id": run_id}),
            headers=headers,
            timeout=10,
        )


def test_parse_error_message():
    response = MagicMock()
    response.json.return_value = {"error": {"message": "An error occurred"}}

    error_message = parse_error_message(response)
    assert error_message == "An error occurred"

    response.json.side_effect = ValueError
    response.text = "Some error text"
    error_message = parse_error_message(response)
    assert error_message == "HTTP error occurred: Some error text"


def test_timedelta_to_iso():
    td = timedelta(days=2, hours=3, minutes=4, seconds=5, microseconds=600000)
    iso_format = timedelta_to_iso(td)
    assert iso_format == "P2DT3H4M5.600000S"


def test_log_and_raise():
    logger = MagicMock()
    with pytest.raises(RuntimeError):
        log_and_raise(logger, "An error occurred")

    logger.error.assert_called_with("An error occurred")
