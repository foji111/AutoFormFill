## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Inconsistent Security Controls]
**Vulnerability:** File size limits were enforced in `aadharcard_routes.py` but missing in `pancard_routes.py` and `marksheet_routes.py`.
**Learning:** Security fixes applied to one part of the codebase must be audit-checked against similar components. Inconsistent application of security controls is a common gap.
**Prevention:** Centralize security constants (like `MAX_FILE_SIZE`) and validation logic instead of duplicating code across routes.
