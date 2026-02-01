## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Inconsistent Security Application]
**Vulnerability:** Security fixes (DoS limits, Error Sanitization) were applied to `aadharcard_routes.py` but missing in `pancard_routes.py` and `marksheet_routes.py`.
**Learning:** Partial security fixes leave the application vulnerable.
**Prevention:** When fixing a class of vulnerability (e.g., DoS), search the entire codebase for similar patterns/endpoints and apply the fix universally.
