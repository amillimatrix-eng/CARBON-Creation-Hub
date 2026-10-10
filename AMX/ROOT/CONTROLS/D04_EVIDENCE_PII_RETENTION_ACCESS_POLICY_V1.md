# D04 EVIDENCE / PII RETENTION & ACCESS POLICY V1
Date: 2026-10-10
Control: SEC07

## Principles
- Data minimization: retain only what is needed to prove the governed claim, execute an authorized obligation, or preserve audit continuity.
- Public-safe projection: private records may support a public claim without exposing the raw private source.
- Secrets are never copied into public evidence.
- Supersession preserves provenance; it does not silently rewrite or discard earlier evidence.
- UNKNOWN/HOLD is preferred over copying sensitive data merely to fill a gap.

## Evidence classes
1. PUBLIC/CANONICAL — repository-safe artifacts, public sources, hashes, non-sensitive receipts.
2. CONTROLLED EVIDENCE — CV source documents, screenshots, payslips, bank statements, private account records, identity/KYC material.
3. SECRET/AUTH MATERIAL — passwords, tokens, OTPs, private keys, security answers. These are not evidence artifacts and must not be persisted into AMX public/canonical stores.
4. PROVIDER RECEIPTS — message IDs, transaction IDs, issue/PR/run IDs; retain identifiers and bounded metadata needed for readback, not unnecessary message/private payload.

## Retention
AMX currently adopts no fabricated fixed legal retention period through this control.
- Public/canonical evidence is retained while it remains part of active provenance or historical continuity.
- Controlled evidence is retained only while needed for its proof/operational purpose or until governed deletion/supersession is authorized.
- Secret/auth material is not retained in evidence stores.
- Deletion requests or legal retention requirements must be handled under the controlling policy/law applicable to the source; this document does not invent one.

## Access
- Controlled evidence is least-access by operational need.
- Public-safe claims must point to hashes/source references rather than reproduce sensitive underlying data.
- Connector/app access remains subject to platform permission and Owner/security authority.
- Reads/writes that materially affect truth should leave durable receipts where the provider supports them.

## Deletion / correction
No worker may silently destroy contradictory or superseded evidence. Correction means: preserve provenance, mark supersession/invalidity, restrict sensitive content where appropriate, and perform governed deletion only when authorized.
