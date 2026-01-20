## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-01-20 - [Memory Exhaustion via File Uploads]
**Vulnerability:** File upload endpoints (`/pan/extract-from-file`, `/marksheet/extract-from-file`) read the entire file into memory with `await file.read()` without checking the size first.
**Learning:** Even if the infrastructure has limits, the application should defend itself. FastAPI's `UploadFile` can be spooled, but `await read()` loads it all.
**Prevention:** Use `file.file.seek(0, 2)` to check `file.file.tell()` (size) before reading content.
