## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2026-01-31 - [Inconsistent Security Application]
**Vulnerability:** DoS vulnerability and Info Leak persisted in `pancard` and `marksheet` routes despite being previously identified.
**Learning:** Security fixes were not propagated to all similar endpoints. Partial fixes create a false sense of security.
**Prevention:** When patching a vulnerability class (like File Upload DoS), audit all other instances of that pattern (e.g., search for all `UploadFile` usages) to ensure comprehensive coverage.
