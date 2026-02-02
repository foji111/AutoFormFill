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

def test_large_file_upload(mock_genai):
    # Create a large file (11MB)
    large_content = VALID_PNG_BYTES + b"A" * (11 * 1024 * 1024)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    # Should not be called
    mock_response.text = '{}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/pan/extract-from-file", files=files)

    # Should be rejected with 413 Payload Too Large
    assert response.status_code == 413, f"Expected 413, got {response.status_code}"
    assert "File too large" in response.json().get("detail", "")

def test_info_leak_on_json_error(mock_genai):
    # Mock a response that is NOT valid JSON and contains sensitive info
    mock_response = MagicMock()
    mock_response.text = 'I am not JSON. This is sensitive info: SECRET_KEY=123'
    mock_genai.return_value.generate_content.return_value = mock_response

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    # Expect 500 error
    try:
        response = client.post("/pan/extract-from-file", files=files)
        assert response.status_code == 500
        error_detail = str(response.json().get("detail", ""))

        # Verify that the raw output IS NOT leaked
        assert "SECRET_KEY=123" not in error_detail
        # Verify we get a structured error message
        assert "error" in response.json().get("detail", {}) or "error" in response.json()
    except Exception as e:
        # If the server crashes or behaves unexpectedly
        pytest.fail(f"Server crashed or returned unexpected response: {e}")
