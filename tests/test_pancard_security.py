
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

def test_pancard_large_file_upload(mock_genai):
    """
    VULNERABILITY TEST: This checks if the API properly rejects large files.
    Currently, pancard_routes.py reads the whole file into memory, so this test fails if the vulnerability exists
    (or rather, if we were really sending a 10GB file, it would crash. Here we check for explicit rejection).
    """
    # Create a large file (11MB) - limit should be 10MB
    large_content = VALID_PNG_BYTES + b"A" * (11 * 1024 * 1024)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    mock_response.text = '{}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/pan/extract-from-file", files=files)

    # If vulnerable, it will likely return 200 (processed) or 500 (memory error if real),
    # but we want to assert it returns 413 Payload Too Large
    assert response.status_code == 413
    assert "File too large" in response.json().get("detail", "")

def test_pancard_info_leak_on_error(mock_genai):
    """
    VULNERABILITY TEST: Checks if exception details are leaked.
    """
    # Mock the response to raise an exception during generation
    mock_genai.return_value.generate_content.side_effect = Exception("Database connection failed at 192.168.1.1")

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/pan/extract-from-file", files=files)

    # We expect a sanitized 500 error
    assert response.status_code == 500
    detail = str(response.json().get("detail", ""))

    # Vulnerability check: The raw exception message should NOT be present
    assert "Database connection failed" not in detail
    assert "192.168.1.1" not in detail
