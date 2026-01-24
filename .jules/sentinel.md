## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Inconsistent Security Implementation]
**Vulnerability:** Security fixes (DoS protection, error sanitization) were applied to some routes (`aadharcard_routes.py`) but not others (`marksheet_routes.py`).
**Learning:** Security controls must be applied consistently across all similar endpoints (e.g., all file upload routes).
**Prevention:** Use shared dependencies or middleware for common security checks (like file size limits) instead of repeating code in each route.
