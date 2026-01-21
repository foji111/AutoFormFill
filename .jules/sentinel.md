## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Consistent Security Application]
**Vulnerability:** Inconsistent application of security fixes (DoS protection) across similar endpoints (`pancard` and `marksheet` routes were missed when `aadhaar` was fixed).
**Learning:** Security fixes must be applied holistically. When a vulnerability pattern is found, grep the entire codebase for similar patterns.
**Prevention:**
1. Use `grep` or search to find all instances of `UploadFile` or similar dangerous sinks.
2. Verify all routes sharing similar logic have the same protections.
