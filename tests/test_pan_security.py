
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

def test_pan_large_file_upload_dos(mock_genai):
    """
    Test that uploading a large file (>10MB) returns 413 Payload Too Large.
    This test is expected to FAIL before the fix.
    """
    # Create a large file (11MB) - simulated
    # Note: We need to be careful not to actually crash the test runner if it reads it all into memory
    # But 11MB is safe for test runner memory.

    large_content = VALID_PNG_BYTES + b"A" * (11 * 1024 * 1024)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    # If the check is missing, it will proceed to call Gemini.
    # We mock Gemini to return a valid response so we get a 200 OK.
    mock_response.text = json.dumps({
        "name": "Test User",
        "pan_number": "ABCDE1234F",
        "date_of_birth": "01/01/2000"
    })
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/pan/extract-from-file", files=files)

    # Before fix: This assertion will fail (it will be 200)
    # After fix: This assertion will pass (it will be 413)
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
