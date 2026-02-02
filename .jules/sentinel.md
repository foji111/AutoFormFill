## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Inconsistent Security Controls]
**Vulnerability:** Security controls (DoS protection, error sanitization) were applied to one endpoint (`/aadhaar`) but missing in others (`/pan`), creating a false sense of security.
**Learning:** Security features must be applied systematically across all similar endpoints rather than ad-hoc per route.
**Prevention:** Use shared utility functions or middleware for common security checks (like file size validation) to ensure coverage.
