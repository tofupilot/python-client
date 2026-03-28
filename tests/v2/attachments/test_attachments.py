"""Test attachment operations."""

import os
import tempfile
from types import SimpleNamespace

import pytest
import requests as http_requests
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND


class TestAttachmentInitialize:
    """Test attachment initialization."""

    def test_initialize_returns_upload_url(self, client: TofuPilot) -> None:
        result = client.attachments.initialize(name="test.txt")
        assert result.id
        assert result.upload_url
        assert "http" in result.upload_url


class TestAttachmentLifecycle:
    """Test the full attachment lifecycle: initialize → upload → finalize."""

    def test_full_lifecycle(self, client: TofuPilot) -> None:
        init = client.attachments.initialize(name="lifecycle_test.txt")

        resp = http_requests.put(
            init.upload_url,
            data=b"lifecycle test content",
            headers={"Content-Type": "text/plain"},
        )
        assert resp.status_code == 200

        result = client.attachments.finalize(id=init.id)
        assert result.url

    def test_finalize_nonexistent_id(self, client: TofuPilot) -> None:
        with pytest.raises(ErrorNOTFOUND):
            client.attachments.finalize(id="00000000-0000-0000-0000-000000000000")


class TestAttachmentUpload:
    """Test the upload() convenience method."""

    def test_upload_file(self, client: TofuPilot) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"convenience method test")
            f.flush()
            path = f.name

        try:
            upload_id = client.attachments.upload(path)
            assert upload_id
            assert len(upload_id) == 36
        finally:
            os.unlink(path)

    def test_upload_nonexistent_file(self, client: TofuPilot) -> None:
        with pytest.raises(FileNotFoundError):
            client.attachments.upload("/tmp/nonexistent_file_abc123.txt")


class TestAttachmentDownload:
    """Test the download() convenience method."""

    def test_download_uploaded_file(self, client: TofuPilot) -> None:
        content = b"round-trip download test"

        # Initialize, upload, finalize manually to get the download URL
        init = client.attachments.initialize(name="download_test.txt")
        http_requests.put(init.upload_url, data=content, headers={"Content-Type": "text/plain"})
        result = client.attachments.finalize(id=init.id)

        attachment = SimpleNamespace(name="download_test.txt", download_url=result.url)

        dest = tempfile.mktemp(suffix=".txt")
        try:
            path = client.attachments.download(attachment, dest=dest)
            assert path.exists()
            assert path.read_bytes() == content
        finally:
            if os.path.exists(dest):
                os.unlink(dest)

    def test_download_no_url(self, client: TofuPilot) -> None:
        attachment = SimpleNamespace(name="missing.txt", download_url=None)
        with pytest.raises(ValueError, match="no download URL"):
            client.attachments.download(attachment)
