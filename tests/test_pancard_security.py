import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import base64

# Mock environment variable BEFORE importing app
os.environ["GOOGLE_API_KEY"] = "AIzaMockKey"

from main import app

client = TestClient(app)

VALID_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
VALID_PNG_BYTES = base64.b64decode(VALID_PNG_B64)

@pytest.fixture
def mock_genai():
    with patch("google.generativeai.GenerativeModel") as mock:
        yield mock

def test_pancard_large_file_upload(mock_genai):
    # Create a large file (11MB)
    large_content = VALID_PNG_BYTES + b"A" * (11 * 1024 * 1024)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    mock_response.text = '{"name": "test", "pan_number": "ABCDE1234F", "date_of_birth": "01/01/2000"}'
    mock_genai.return_value.generate_content.return_value = mock_response

    # This should fail initially (likely 200 OK because of mock, or crash), but we expect 413 after fix
    response = client.post("/pan/extract-from-file", files=files)

    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_pancard_info_leak(mock_genai):
    # Test for info leak on exception
    mock_response = MagicMock()
    # This will cause json parse error
    mock_response.text = "Not JSON"
    mock_genai.return_value.generate_content.return_value = mock_response

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}
    response = client.post("/pan/extract-from-file", files=files)

    assert response.status_code == 500
    assert response.json()["detail"] == "Error processing image data."
