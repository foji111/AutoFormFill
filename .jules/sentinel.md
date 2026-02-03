## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Inconsistent Security Controls]
**Vulnerability:** While file size limits were documented, they were only implemented in `aadharcard_routes.py`, leaving `pancard_routes.py` and `marksheet_routes.py` vulnerable.
**Learning:** Manual implementation of security controls in each controller leads to inconsistencies.
**Prevention:** Verify security controls across *all* endpoints, not just the first one. Consider using shared dependencies for common security logic.
