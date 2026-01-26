
import os
import json
import base64
import pytest
from unittest.mock import MagicMock, patch

# Mock environment variable BEFORE importing app
os.environ["GOOGLE_API_KEY"] = "AIzaMockKey"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Valid 1x1 PNG
VALID_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
VALID_PNG_BYTES = base64.b64decode(VALID_PNG_B64)

@pytest.fixture
def mock_genai():
    with patch("google.generativeai.GenerativeModel") as mock:
        yield mock

def test_info_leak_on_error(mock_genai):
    # Mock a generic exception that contains sensitive info
    mock_genai.return_value.generate_content.side_effect = Exception("DB_PASSWORD=secret123")

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/marksheet/extract-from-file", files=files)

    # Expect 500 error
    assert response.status_code == 500
    error_detail = response.json()["detail"]

    # This assertion will FAIL if the vulnerability exists (because "DB_PASSWORD=secret123" WILL be present)
    assert "DB_PASSWORD=secret123" not in str(error_detail), "Sensitive info leaked in error response!"
    assert "An unexpected error occurred" in str(error_detail) or "Error processing image" in str(error_detail)

def test_large_file_upload(mock_genai):
    # Create a large file (11MB) - we won't actually send 11MB over the wire if we can avoid it,
    # but with TestClient it's in memory.
    # To avoid OOM in this environment, let's trust the seek check logic if we implement it.
    # But for the reproduction, we need to send enough to trigger the check if it existed.
    # Since we are adding a check for > 10MB, we need > 10MB.

    # WARNING: This might be slow.
    large_content = b"A" * (10 * 1024 * 1024 + 1)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    mock_response.text = '{}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/marksheet/extract-from-file", files=files)

    # This assertion will FAIL if the vulnerability exists (likely returns 200 or 500)
    assert response.status_code == 413, f"Expected 413, got {response.status_code}"
