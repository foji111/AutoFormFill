## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Inconsistent Security Application]
**Vulnerability:** DoS protection (MAX_FILE_SIZE) was implemented in one route but missing in others, leaving the app vulnerable.
**Learning:** Security fixes must be audited across the entire codebase, not just the file where the issue was first found.
**Prevention:** When fixing a vulnerability pattern, grep for similar code/endpoints and apply the fix universally.
