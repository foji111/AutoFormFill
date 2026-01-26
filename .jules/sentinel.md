## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-05-22 - [Inconsistent Security Controls]
**Vulnerability:** `marksheet_routes.py` lacked security controls (size limit, error sanitization) that were present in `aadharcard_routes.py`.
**Learning:** Security fixes must be applied horizontally across all similar endpoints. Fixing one route does not automatically fix others.
**Prevention:** Use shared middleware or base classes for common security logic (like file size checks and error handling) instead of duplicating code in each route.
