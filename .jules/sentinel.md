## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Observability & Error Handling]
**Vulnerability:** Silent failure when sanitizing errors.
**Learning:** Returning generic 500 errors without server-side logging hides critical failure information from developers, making debugging impossible.
**Prevention:**
1. Always log the full exception stack trace to the server logs (`logger.error`) before raising a sanitized `HTTPException`.
