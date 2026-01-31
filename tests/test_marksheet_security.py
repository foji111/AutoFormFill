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

def test_marksheet_large_file_upload(mock_genai):
    # Create a large file (11MB)
    large_content = VALID_PNG_BYTES + b"A" * (11 * 1024 * 1024)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    # Return minimal valid marksheet json
    mock_response.text = '{"student_name": "Test", "enrollment_number": "123", "university_name": "Uni", "program_name": "Prog", "semester": "I", "results": [], "result_status": "Pass"}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/marksheet/extract-from-file", files=files)

    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_marksheet_info_leak(mock_genai):
    # Test for info leak on exception
    mock_response = MagicMock()
    # This will cause json parse error
    mock_response.text = "Not JSON"
    mock_genai.return_value.generate_content.return_value = mock_response

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}
    response = client.post("/marksheet/extract-from-file", files=files)

    # We expect 500, but we want to ensure the detail doesn't leak raw exception str(e)
    # The current code leaks "Error processing image: ... expecting value ..."
    # We want it to be sanitized.
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred while processing the image."
