import os
import io
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

os.environ["GOOGLE_API_KEY"] = "AIzaMockKey"

from main import app

client = TestClient(app)

LARGE_FILE_SIZE = 11 * 1024 * 1024
LARGE_CONTENT = b"A" * LARGE_FILE_SIZE

@pytest.fixture
def mock_genai():
    with patch("pancard_routes.genai.GenerativeModel") as mock:
        yield mock

def test_pancard_large_file_upload(mock_genai):
    files = {"file": ("large.png", LARGE_CONTENT, "image/png")}

    mock_response = MagicMock()
    mock_response.text = '{"name": "Test", "pan_number": "ABCDE1234F", "date_of_birth": "01/01/1990"}'
    mock_genai.return_value.generate_content.return_value = mock_response

    response = client.post("/pan/extract-from-file", files=files)

    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
