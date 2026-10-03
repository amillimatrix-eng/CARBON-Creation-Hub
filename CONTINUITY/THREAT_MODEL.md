# Continuity and capability threat model

Assets: governance, source assets, production, commercial records, credentials,
recoverable caches, historical provenance, grants and accepted receipts.

Trust boundaries: provider accounts; public Git; BLACK service identity; recovery
key custody; encrypted disk/replica; authorized Root/Critic promotion; public House.
Drive is a capable provider, but concentrating recoverability there exposes the
estate to account/permission/API/provider failures. Availability is not authority.

| Threat | Control | Remaining dependency |
| --- | --- | --- |
| Account compromise, permission drift, deletion, revoked connector | Immutable encrypted generations, pin hashes, per-source failures, bounded fallback | Least-privilege Drive enrollment and inventory completion |
| Ransomware/disk loss | Authenticated encryption, explicit retention, independent ciphertext replication | Physically independent destination and offline key escrow |
| Corruption/poisoned backup | Per-chunk/file/manifest hashes, expected authority hash, full verification before latest promotion | Compromised authority must be reconciled by Root; hashes alone do not prove legitimacy |
| Incomplete sync/conflicting writes | Exclusive process lock, atomic publication, immutable version IDs, keep prior verified snapshot | Disk space and filesystem semantics |
| Stale restore/provider outage | Snapshot age, per-source timestamps, explicit degraded/HOLD; isolated restore and comparison | Source revalidation when provider returns |
| Key or credential compromise | Secret files outside Git, 0600, service scope, no raw output/public inventory | Rotation and escrow custody require legitimate account owner/admin |
| Public queue command injection | Typed adapters, exact command digest grants, deployment separate from queue sync | Authorized grants must remain protected locally |
| Worker drift/self-modification | Typed evidence, tests, Root promotion, version CAS, fixed mandate hash | Governance authentication/persistent EvidenceStore |
| Public API disclosure | Private versions filtered, authenticated inventory/learning writes, allowlisted health | Existing public commercial fields require ongoing owner review |
| Provider-generated rights errors | Quarantine, source checks, rebuild/re-render + Critic before market master | Rights/attribution acceptance evidence |

No remote shell, arbitrary source URL, target exploitation, transaction signing,
spend, outreach, or production deployment is conferred by this control plane.
Encryption uses the installed cryptography library; no cipher is implemented here.
Hash chains detect modification relative to a trusted anchor; they are not a
substitute for independent immutable custody against a fully compromised host.
