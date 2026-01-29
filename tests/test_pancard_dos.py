
import os
import io
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Mock environment variable BEFORE importing app to avoid import errors if keys are checked at module level
os.environ["GOOGLE_API_KEY"] = "AIzaMockKey"

from main import app

client = TestClient(app)

@pytest.fixture
def mock_genai():
    with patch("google.generativeai.GenerativeModel") as mock:
        yield mock

def test_pancard_large_file_upload(mock_genai):
    """
    Test that uploading a file larger than 10MB to the PAN card extraction endpoint
    returns a 413 Request Entity Too Large error.
    """
    # Create a large file content (10MB + 1 byte)
    # specific size: 10 * 1024 * 1024 + 1
    large_content = b"A" * (10 * 1024 * 1024 + 1)

    files = {"file": ("large_pan.png", large_content, "image/png")}

    # Mock the Gemini response just in case execution gets there (it shouldn't if we block it)
    mock_response = MagicMock()
    mock_response.text = '{"name": "Test", "pan_number": "ABCDE1234F", "date_of_birth": "01/01/1990"}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/pan/extract-from-file", files=files)

    # We expect 413 Payload Too Large
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
