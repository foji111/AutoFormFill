
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
    mock_response.text = '{}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/marksheet/extract-from-file", files=files)

    # Should be rejected with 413 Payload Too Large
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_info_leak_on_error(mock_genai):
    # Mock a failure in Gemini (raising an exception)
    mock_genai.return_value.generate_content.side_effect = Exception("Internal Database Connection Failed at IP 192.168.1.5")

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/marksheet/extract-from-file", files=files)

    # Expect 500 error
    assert response.status_code == 500
    error_detail = response.json()["detail"]

    # Verify that the raw output IS NOT leaked
    # Currently it leaks "Error processing image: Internal Database Connection Failed at IP 192.168.1.5"
    assert "192.168.1.5" not in str(error_detail)
    assert "Internal Database Connection Failed" not in str(error_detail)
    assert error_detail == "An internal error occurred."
