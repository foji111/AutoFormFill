## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-26 - [Inconsistent Security Implementation]
**Vulnerability:** New routes (`pancard_routes.py`, `marksheet_routes.py`) were introduced without the DoS protections present in existing routes (`aadharcard_routes.py`).
**Learning:** Security controls must be applied consistently across all similar endpoints. Copy-pasting code often misses security contexts if not explicitly checked.
**Prevention:**
1. Use shared dependencies or middleware for common security checks (like file size limits) instead of repeating logic in every route.
2. Ensure new endpoints have security unit tests (e.g. large file upload tests) before merging.
