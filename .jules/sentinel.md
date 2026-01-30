## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [Base64 DoS Prevention]
**Vulnerability:** Base64 encoded uploads can also cause DoS if decoded into memory without size checks.
**Learning:** Checking `len(base64_string) * 0.75` provides a cheap, effective approximate size check before expensive decoding.
**Prevention:** Always validate Base64 string length against `MAX_FILE_SIZE / 0.75` (or similar heuristic) before `base64.b64decode`.
