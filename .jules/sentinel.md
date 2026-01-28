## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Unchecked File Upload Memory Exhaustion]
**Vulnerability:** `UploadFile.read()` reads the entire file into memory. Without a prior size check, this allows DoS via RAM exhaustion.
**Learning:** FastAPI/Starlette `UploadFile` exposes the underlying `SpooledTemporaryFile` via `.file`. We must use `.seek(0, 2)` and `.tell()` to check size *before* calling `.read()`.
**Prevention:** Enforce `MAX_FILE_SIZE` check on all file upload endpoints using `seek/tell`.
