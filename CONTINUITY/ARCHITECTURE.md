# Existing Matrix with continuity extensions

```mermaid
flowchart LR
  G[Governed Drive sources] --> R[Explicit source registry]
  V[Git repositories and accepted receipts] --> R
  C[Authoritative configuration] --> R
  R --> B[Existing BLACK: bounded sync adapters]
  B --> E[Encrypted chunks and versioned manifests]
  E --> T[Verify and restore into a clean target]
  T --> Q[Immutable encrypted receipts]
  B --> Q
  Q --> H[Existing evidence backend and House operator state]
  W[Existing workers including independent Bounty Reaper] --> L[EvidenceStore governed learning]
  L --> K[Critic tests and authorized versioned promotion]
  K --> W
```

Root retains reconciliation authority. OVERDRIVE retains transport/evidence routing.
Mirrors retain source authority metadata but carry `role=MIRROR_RECOVERY` themselves.
No provider or recovery copy becomes Canon by being available. Historical
black-control remains provenance; installation must not activate it alongside BLACK.
The existing live House stays the operator surface; private recovery inventory is
authenticated/local, public health contains only an explicit safe field set.
