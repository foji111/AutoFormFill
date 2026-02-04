
import os
import io
import base64
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

# Set Mock API Key
os.environ["GOOGLE_API_KEY"] = "AIzaMockKey"

client = TestClient(app)

# Valid 1x1 PNG
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
    mock_response.text = '{}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/marksheet/extract-from-file", files=files)

    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_marksheet_info_leak_error(mock_genai):
    # Simulate a generic exception in the logic
    # We mock the model to raise an exception with sensitive info
    mock_genai.return_value.generate_content.side_effect = Exception("Sensitive internal DB info")

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/marksheet/extract-from-file", files=files)

    assert response.status_code == 500
    error_detail = response.json()["detail"]

    # Verify that the raw output IS NOT leaked anymore
    assert "Sensitive internal DB info" not in str(error_detail)
    # It should have a generic message
    assert "An unexpected error occurred" in str(error_detail)
