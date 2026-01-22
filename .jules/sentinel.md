## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [DoS Protection & Exception Handling]
**Vulnerability:** DoS vulnerability via unchecked file uploads in PAN and Marksheet routes. Also, potential exception swallowing when using `except Exception` which catches `HTTPException`.
**Learning:** `except Exception` catches `HTTPException` (which inherits from Exception). Always handle specific `HTTPException` before generic `Exception` to avoid masking intentional error responses (like 413).
**Prevention:**
1. Use `except HTTPException: raise` before catch-all `except Exception`.
2. Enforce `MAX_FILE_SIZE` using `file.seek(0, 2)` before reading content.
