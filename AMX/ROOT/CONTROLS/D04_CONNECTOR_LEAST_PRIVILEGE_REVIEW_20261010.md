# D04 CONNECTOR LEAST-PRIVILEGE REVIEW — 2026-10-10
Control: SEC02

Observed plugin permission readback during the D04/FORX run showed broad "allow all actions" posture for several critical connected apps, including GitHub, Gmail, Close, TinyFish and Google Drive.

## Required operational classes
- GitHub: canonical read/write, issue/PR/workflow evidence and bounded mutations.
- Gmail: search/read threads, send/reply when PRI/commercial mandate authorizes.
- Close: bounded projection read/write only.
- TinyFish/browser: public/browser execution only when route is authorized.
- Drive/Library: controlled evidence read; writes only where explicit destination/authority exists.
- Stripe/payment provider: settlement read and bounded authorized payment objects; no unrelated account changes.

## Disposition
PARTIAL / OWNER-SECURITY-GATED.

This review deliberately does NOT auto-restrict permissions. Blindly changing connector permissions can break critical continuity and is itself consequential. Permission reduction requires Owner/security authority with an exact per-app allowlist and recovery plan.

## Acceptance still required
Document and approve final per-app permission posture; then read back the applied permissions. Until that happens SEC02 remains PARTIAL.
