
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

def test_upload_valid_file(mock_genai):
    # Mock the response from Gemini
    mock_response = MagicMock()
    mock_response.text = '{"name": "Test User", "aadhar_number": "123456789012", "date_of_birth": "01/01/2000", "gender": "Male", "guardian_or_care_of": "Father", "address": "123 Street"}'
    mock_genai.return_value.generate_content.return_value = mock_response

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/aadhaar/extract-from-file", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"

def test_info_leak_on_json_error(mock_genai):
    # Mock a response that is NOT valid JSON
    mock_response = MagicMock()
    mock_response.text = 'I am not JSON. This is sensitive info: SECRET_KEY=123'
    mock_genai.return_value.generate_content.return_value = mock_response

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/aadhaar/extract-from-file", files=files)

    # Expect 500 error
    assert response.status_code == 500
    error_detail = response.json()["detail"]

    # Verify that the raw output IS NOT leaked anymore
    assert "SECRET_KEY=123" not in str(error_detail)
    assert "Failed to parse JSON output" in str(error_detail)

def test_large_file_upload(mock_genai):
    # Create a large file (11MB)
    large_content = VALID_PNG_BYTES + b"A" * (11 * 1024 * 1024)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    # Should not be called
    mock_response.text = '{}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/aadhaar/extract-from-file", files=files)

    # Should be rejected with 413 Payload Too Large
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
