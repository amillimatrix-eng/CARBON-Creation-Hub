# Provider dependency and failure/recovery map

| Failure | Detection/evidence | Bounded recovery and authority rule |
| --- | --- | --- |
| Google unavailable, API changed or OAuth revoked | Per-source export/inventory failure; encrypted sync receipt and source failure count | Keep previous inventory/generations; restore verified bytes offline; retry bounded export; restored mirror never becomes governance |
| GitHub unavailable | BLACK queue fetch/publication failure; outbox and deployed source commit | Pinned executable remains usable; encrypted local recovery and receipts survive; retry outbox before queue polling |
| Render unavailable | Existing House health/readback failure | Existing backend runs from a clean local checkout; Git/BLACK preserve state; free SQLite runtime remains unsuitable for accepted mutable production custody |
| OpenAI unavailable | Provider action failure | Continuity, evidence search and filtering require no model/API key; provider intelligence is advisory |
| BLACK offline | Stale health/receipt age | Preserve capability as HOLD; existing workers retain ownership; resume existing node and validate latest snapshot |
| BLACK disk loss | Missing ciphertext/key/store; independent replica verification | Restore independent encrypted copy and separately escrowed key; same-device test copies are never disaster-recovery evidence |
| Network unavailable | Source-specific failures, local outbox | Read already-verified mirror and pinned code; no inferred new provider state |
| Credentials revoked/compromised | Failure class + issuer/account evidence | Revoke/rotate legitimately, replace scoped local binding, retain all unrelated capabilities; no credentials through chat/Git |
| Corrupt mirror | Fernet authentication/hash failure, FAIL receipt | Refuse promotion/overwrite; restore an explicitly verified older generation; retain corrupt evidence for reconciliation |
| Stale mirror | Backup/health age and observed source versions | Bounded read-only degraded state; revalidate when source returns; freshness cannot be fabricated by a heartbeat |
| Incomplete sync | No atomic latest promotion; orphan chunks/immutable manifests retained | Re-run converges; prior verified snapshot survives; failed required sources cannot claim full-estate restoration |
| Provider API change | Adapter error; no empty-inventory deletion | Retain old source IDs and exports, adjust the bounded adapter under version control, re-test |
| Worker crash | Journal/outbox/lock state | Safe adapters resume; interrupted consequential shell command becomes reconciliation HOLD, never a blind replay |
| Conflicting writes | Lock/CAS, source stat change, registry/command pin mismatch | Refuse divergent source or capability promotion; preserve both evidence versions; Root resolves authority |

Portable state: repository text/JSON/source, SQLite online backup, native Drive
text/XLSX/PDF exports, original binary assets, lifecycle/rights manifests and receipts.
Provider-specific assumptions: Drive export formats/scoped remote and ID inventory;
GitHub Contents API/job queue; Render's free ephemeral volume; Windows/WSL startup.
Google authentication is required only to refresh, not to decrypt/restore a snapshot.
Recovery key and independently stored ciphertext are both needed after BLACK disk loss.

Automatic Drive inventory enrollment preserves stable provider IDs and accepted
classification, appends new references, and retains vanished entries. Unknown
classification stays a governance HOLD rather than inventing Canon. Provider identity
is provenance; project/lifecycle remains the production organization principle.
