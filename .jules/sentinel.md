## 2025-10-26 - [DoS & Info Leak Prevention]
**Vulnerability:** The application was vulnerable to Denial of Service (DoS) via large file uploads (no size limit) and Information Leakage (exposing raw LLM output in 500 errors).
**Learning:** Checking file content type is not enough; explicit size limits are required. Exposing raw error/output in API responses can leak internal state or secrets.
**Prevention:**
1. Always enforce `MAX_FILE_SIZE` on uploads.
2. Sanitize error messages in `HTTPException` to hide internal details.

## 2025-10-27 - [PAN Card Route Security Hardening]
**Vulnerability:** `pancard_routes.py` lacked file size validation (DoS risk) and leaked raw exception details in 500 errors (Info Leakage), inconsistent with `aadharcard_routes.py`.
**Learning:** Security controls must be applied consistently across all API routes. A secure pattern in one module doesn't automatically protect others.
**Prevention:**
1. Applied `MAX_FILE_SIZE` (10MB) check in `pancard_routes.py`.
2. Wrapped external API calls in `try/except` blocks to catch and sanitize exceptions.
