
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

def test_large_file_upload_pan(mock_genai):
    """
    Test that uploading a file larger than 10MB is rejected with 413.
    """
    # Create a large file (11MB)
    large_content = VALID_PNG_BYTES + b"A" * (11 * 1024 * 1024)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    # If the validation is missing, it will proceed to call Gemini (or mock)
    mock_response.text = '{"name": "Test", "pan_number": "ABCDE1234F", "date_of_birth": "01/01/2000"}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/pan/extract-from-file", files=files)

    # Should be rejected with 413 Payload Too Large
    assert response.status_code == 413, f"Expected 413, got {response.status_code}"
    assert "File too large" in response.json().get("detail", ""), "Error message mismatch"
