
from fastapi.testclient import TestClient
from main import app
import io
import pytest

client = TestClient(app)

# 10MB + 1 byte
LARGE_SIZE = 10 * 1024 * 1024 + 1

@pytest.mark.parametrize("endpoint", [
    "/pan/extract-from-file",
    "/marksheet/extract-from-file",
    "/aadhaar/extract-from-file"
])
def test_large_file_upload_rejection(endpoint):
    # We use a generator to simulate a large stream without consuming too much memory in the test process if possible,
    # but TestClient/httpx might read it all. 11MB is fine for modern machines.
    large_content = b"0" * LARGE_SIZE

    files = {"file": ("large_image.png", io.BytesIO(large_content), "image/png")}

    response = client.post(endpoint, files=files)

    # Expect 413 Request Entity Too Large
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
