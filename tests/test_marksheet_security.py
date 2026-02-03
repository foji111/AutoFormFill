import os
import io
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Mock environment variable BEFORE importing app
os.environ["GOOGLE_API_KEY"] = "AIzaMockKey"

from main import app

client = TestClient(app)

# 1x1 PNG pixel
VALID_PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"

@pytest.fixture
def mock_genai():
    with patch("google.generativeai.GenerativeModel") as mock:
        yield mock

def test_marksheet_large_file_upload(mock_genai):
    # Create a large file (> 10MB)
    large_content = VALID_PNG_BYTES + b"A" * (10 * 1024 * 1024 + 100)
    files = {"file": ("large.png", large_content, "image/png")}

    mock_response = MagicMock()
    mock_response.text = '{"student_name": "test", "enrollment_number": "123", "university_name": "Uni", "program_name": "Prog", "results": [], "result_status": "Pass"}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/marksheet/extract-from-file", files=files)

    # Should be rejected with 413 Payload Too Large
    assert response.status_code == 413
    assert "File too large" in response.json().get("detail", "")
