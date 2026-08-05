# ADR-0009: Strict Loopback-Only Access

* **Status:** Proposed — pending independent Phase 1B audit
* **Date:** 2026-08-05
* **Context:** Phase 1B establishes the HTTP client for connecting to local models. Allowing connections to any endpoint could introduce network spoofing, Server-Side Request Forgery (SSRF), or accidental exposure to untrusted public APIs.
* **Decision:** We mandate strict loopback-only validation (`127.0.0.0/8`, `::1`, `localhost`) for model endpoints within `SentinelSettings`. Connections to LAN addresses, `0.0.0.0`, or public IPs are rejected during configuration initialization.
* **Evidence:** `SentinelSettings` validations in `sentinelrag.config.settings` and passing tests in `test_settings.py`.
* **Alternatives:** Validating IPs during HTTP request time. Rejected because early failure during configuration is safer and provides clearer errors.
* **Security consequences:** Reduces exposure to non-local endpoints, but explicitly retains residual risks from compromised local services, local malware, future configuration changes, or incorrect future proxying.
* **Operational consequences:** Requires local deployment of the models (or SSH tunneling bounded to localhost).
* **Revisit conditions:** Revisit if/when the architecture mandates dedicated model servers on isolated LAN subnets.
