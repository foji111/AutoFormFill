
import os
import io
import pytest
import base64
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Mock env before importing app
os.environ["GOOGLE_API_KEY"] = "AIzaMockKey"

from main import app

client = TestClient(app)

# Valid 1x1 PNG
VALID_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
VALID_PNG_BYTES = base64.b64decode(VALID_PNG_B64)

@pytest.fixture
def mock_genai():
    # Use patch.dict to ensure we don't break other tests if they rely on specific models,
    # but here we just mock the module.
    # Note: pancard_routes imports 'google.generativeai' as 'genai'.
    # We need to mock 'google.generativeai.GenerativeModel'.
    with patch("google.generativeai.GenerativeModel") as mock:
        yield mock

# --- PAN CARD TESTS ---

def test_pan_large_file_upload_fix(mock_genai):
    """
    Verification: 413 should be returned.
    """
    large_content = b"A" * (11 * 1024 * 1024)
    # Just prepend PNG header
    large_content = VALID_PNG_BYTES + large_content

    files = {"file": ("large.png", large_content, "image/png")}

    response = client.post("/pan/extract-from-file", files=files)

    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_pan_sanitized_exception(mock_genai):
    """
    Verification: 500 returned with sanitized message.
    """
    mock_response = MagicMock()
    mock_response.text = 'NOT JSON'
    mock_genai.return_value.generate_content.return_value = mock_response

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/pan/extract-from-file", files=files)
    assert response.status_code == 500
    assert response.json()["detail"] == "Error processing image"

# --- MARKSHEET TESTS ---

def test_marksheet_large_file_upload_fix(mock_genai):
    """
    Verification: 413 should be returned.
    """
    large_content = b"A" * (11 * 1024 * 1024)
    large_content = VALID_PNG_BYTES + large_content
    files = {"file": ("large.png", large_content, "image/png")}

    response = client.post("/marksheet/extract-from-file", files=files)
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_marksheet_no_info_leak(mock_genai):
    """
    Verification: Error message should NOT contain raw exception details.
    """
    mock_response = MagicMock()
    mock_response.text = 'NOT JSON'
    mock_genai.return_value.generate_content.return_value = mock_response

    files = {"file": ("test.png", VALID_PNG_BYTES, "image/png")}

    response = client.post("/marksheet/extract-from-file", files=files)

    assert response.status_code == 500
    assert response.json()["detail"] == "Error processing image"
