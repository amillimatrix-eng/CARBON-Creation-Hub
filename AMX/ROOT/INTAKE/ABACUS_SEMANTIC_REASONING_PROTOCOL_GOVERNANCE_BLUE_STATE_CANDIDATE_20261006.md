# ABACUS SEMANTIC REASONING PROTOCOL
## Governance + Blue State Merge Candidate

**Date:** 2026-10-06  
**Authority:** OWNER ACCEPTED  
**Priority:** P0 / BLACK-BOX-TOP ROUTE  
**Lifecycle:** ACCEPTED → INDEXED MERGE CANDIDATE  
**Security owner:** FORX  
**Primary destinations:** T-GOV + BLUE STATE  
**Technical destination if authorized:** T-COD / existing BUILD owner  
**Canon effect:** NONE until separately governed  
**Build effect:** NONE until authorized implementation reaches Master Build  
**New architecture:** NO — security/continuity refinement of existing FORX + Governance + Blue State controls

---

## 1. PURPOSE

The Abacus Semantic Reasoning Protocol protects sensitive AMiLLiMATRiX internal meaning while preserving enough structure for authorized systems to reason, resume, verify, and act.

It is designed for internal information that is valid and useful inside the Matrix but must not automatically surface in:
- public explanations;
- NotebookLM-style presentation layers;
- external demos;
- shared documents;
- third-party tools;
- model-visible context that does not require full internal detail.

Core principle:

> **MEANING MAY BE STRUCTURALLY AVAILABLE WITHOUT BEING PUBLICLY DISCLOSED.**

---

## 2. WHAT THE ABACUS IS

The Abacus is not a home-made cipher.

It is a **semantic coordinate / tokenization layer** placed over sensitive Matrix concepts and relationships.

A protected concept is represented by structured coordinates rather than public-language meaning.

Example structure:

`DOMAIN / CONCEPT / RELATION / STATE / AUTHORITY / VISIBILITY / VERSION / EPOCH`

A token such as:

`R7.C3.E2.S4.A1.V0.K2`

has no public meaning without the authorized semantic map.

The token alone must never be treated as cryptographic protection.

---

## 3. CRYPTOGRAPHIC BOUNDARY

Production confidentiality must use established authenticated encryption.

Preferred implementation families:
- XChaCha20-Poly1305; or
- AES-256-GCM.

The Abacus layer provides:
- semantic indirection;
- compartmentalization;
- visibility classification;
- relationship preservation;
- versioning;
- rotation.

Modern AEAD provides:
- confidentiality;
- integrity;
- tamper detection.

Therefore:

> **ABACUS TOKENIZATION ≠ ENCRYPTION.**

No production master secret, private key, recovery phrase, API credential, or plaintext semantic map may be committed to the repository.

---

## 4. SEMANTIC COORDINATE MODEL

Each protected item may contain:

- `domain`
- `concept`
- `relation`
- `state`
- `authority`
- `visibility`
- `version`
- `epoch`
- `provenance_ref`
- `canonical_hash`
- `continuity_weight` where materially required

The model must preserve **relationships**, not merely isolated words.

This aligns with the current Matrix durability finding:

> intelligence often lives in the edges between entities, not the entities alone.

---

## 5. RODS / DOMAINS

Abacus "rods" represent protected semantic domains.

Examples may include:
- Governance;
- Security;
- Commercial Intelligence;
- Capability State;
- Provenance;
- Worker State;
- Internal Metrics;
- Continuation State;
- Routing;
- Verification.

These are classifications, not new architectural layers.

A new rod requires:
- an existing owner;
- a material confidentiality need;
- no duplicate responsibility;
- defined visibility;
- defined key compartment;
- defined retention/rotation policy.

---

## 6. VISIBILITY CLASSES

Minimum visibility classes:

### V0 — FORX / MASTER INTERNAL
Highest internal sensitivity.

### V1 — GOVERNED SPECIALIST
Minimum necessary content for T-GOV / T-COD / authorized specialist execution.

### V2 — INTERNAL OPERATIONAL
Safe for authorized Matrix workers but not public.

### V3 — SANITIZED PRESENTATION
Approved abstraction for T-MED / internal presentation tooling.

### V4 — PUBLIC
Explicitly cleared public content.

Default for protected internal material:

> **V0 / V1 unless explicitly downgraded by authority.**

No model may infer that "accurate" means "public."

---

## 7. COMPARTMENTALIZATION

Different semantic domains should use separate key derivation compartments where practical.

Compromise of one domain must not automatically expose:
- Governance;
- Commercial Intelligence;
- Security;
- Capability State;
- FORX methods;
- unrelated internal metrics.

Key separation must follow existing access/authority ownership.

---

## 8. ROTATION / EPOCHS

Mappings are versioned and rotatable.

Each encoded object records:
- semantic schema version;
- mapping epoch;
- key version reference;
- canonical provenance reference.

Rotation may occur because of:
- exposure;
- scheduled security maintenance;
- material schema change;
- authority change;
- supersession.

Old epochs remain decryptable only where provenance/continuity requires it.

Chronology does not override authority.

---

## 9. CANONICALIZATION BOUNDARY

The existing canonicalization rule remains controlling:

> canonicalization is serialization, not interpretation.

Therefore Abacus must **not** silently alter canonical evidence.

Correct relationship:

**RAW EVIDENCE  
→ governed extraction  
→ canonical representation + canonical hash  
→ Abacus protection wrapper / semantic token layer  
→ encrypted protected storage / transport**

The protected object should preserve the canonical hash of the underlying authorized representation.

Decryption must allow the authorized system to recover the same governed semantic object, not a reinterpreted summary.

---

## 10. BLUE STATE RESPONSIBILITY

Blue State should own the continuity requirements for protected semantic state.

It must ensure:
- semantic coordinates survive restart/handoff;
- relationship edges survive;
- mapping/version provenance survives;
- capability state does not collapse into meaningless tokens;
- authorized systems can reconstruct the material reasoning state;
- deprecated epochs cannot silently override later authorized state.

This extends existing Durable Cognition / Capability Persistence logic rather than creating a new persistence subsystem.

---

## 11. GOVERNANCE RESPONSIBILITY

Governance should own:

- classification rules;
- visibility classes;
- authority to disclose/declassify;
- epoch/version policy;
- provenance requirements;
- supersession;
- retention;
- key-ownership policy;
- allowed public abstractions;
- audit requirements;
- breach/exposure response.

FORX remains security owner and forensic verifier.

---

## 12. FORX RESPONSIBILITY

FORX:

- identifies protected internal information;
- detects disclosure risk;
- assigns/proposes semantic classification;
- builds sanitization packets;
- verifies minimum-necessary disclosure;
- tests whether public/presentation systems can reconstruct protected logic improperly;
- detects stale mappings;
- detects cross-compartment leakage;
- verifies rotation after exposure;
- reports consolidated security truth to Master only.

FORX does not become the cryptographic key custodian merely by owning security governance.

---

## 13. SANITIZATION GATE

Any material flowing toward:
- T-MED;
- public documents;
- NotebookLM;
- public AI explanations;
- demos;
- external summaries;
- public websites;
- marketing;
- media;

must pass a visibility-resolution step.

Protected semantic coordinates are resolved only to the highest disclosure level authorized for the destination.

Example:

Internal:
`COMMERCIAL / BUYER_WEIGHT / LATE_STAGE / V0`

Public abstraction:
> "The system prioritizes relevant active opportunities."

The public layer must not receive the private weighting recipe unless explicitly cleared.

---

## 14. IMPLEMENTABLE DATA ENVELOPE

Suggested protected envelope:

```json
{
  "abacus_version": "asrp-v1",
  "epoch": "E001",
  "domain": "opaque-domain-token",
  "semantic_token": "opaque-token",
  "visibility": "V1",
  "authority_ref": "governed-authority-ref",
  "provenance_ref": "artifact-or-ledger-ref",
  "canonical_hash": "sha256-of-governed-plaintext-representation",
  "key_ref": "non-secret-key-reference",
  "cipher": "XCHACHA20-POLY1305-or-AES-256-GCM",
  "ciphertext": "...",
  "aad": {
    "version": "asrp-v1",
    "visibility": "V1",
    "epoch": "E001"
  }
}
```

No secret key material appears in this envelope.

---

## 15. REQUIRED IMPLEMENTATION COMPONENTS

If T-GOV authorizes implementation, T-COD should produce:

1. semantic schema;
2. mapper/tokenizer;
3. encrypted map-vault interface;
4. key-provider abstraction;
5. visibility resolver;
6. sanitizer;
7. encoder;
8. decoder;
9. epoch rotation mechanism;
10. provenance/canonical-hash validator;
11. access-control integration;
12. audit event interface;
13. test fixtures;
14. migration path for protected existing records.

---

## 16. KEY MANAGEMENT

Preferred production design:
- external KMS/HSM/OS-secure-secret provider where available;
- least-privilege key access;
- domain-separated derivation;
- key versioning;
- no secrets in GitHub;
- no secrets in transcript;
- no secrets in public docs;
- no secrets in model-readable test fixtures.

Fallback implementations must be explicitly classified non-production if they cannot meet this boundary.

---

## 17. ROLLING CONSENSUS INTEGRATION HOOK

The current governed corpus searched during this intake pass did **not** yield an authoritative artifact defining "rolling consensus."

Therefore this protocol does not invent its mechanics.

If an existing accepted Rolling Consensus control is recovered, Abacus should integrate by consuming only its **authorized resolved state** where relevant to:
- classification;
- semantic mapping;
- visibility;
- epoch/supersession;
- relationship confidence.

Abacus must not create an independent voting/consensus architecture.

Required future reconciliation:

`ROLLING_CONSENSUS_SOURCE = UNRESOLVED / RECOVER EXACT ARTIFACT`

---

## 18. BLACK-BOX ROUTING INTERPRETATION

The Owner directed this protocol "directly to the black box, right on top."

No separate governed BLACK BOX subsystem was recovered in the current repository search.

To avoid inventing architecture, this instruction is implemented as:

> **TOP-OF-INTAKE / P0 GOVERNANCE + BLUE STATE ROUTING**

"Black box" is preserved as Owner routing language, not treated as a new BLACK architectural layer or new office.

If an existing Black Box artifact is later recovered, FORX must reconcile this candidate into that exact owner without duplicating responsibility.

---

## 19. SECURITY FAILURE TESTS

Acceptance tests must include:

- unauthorized presentation model cannot resolve protected coordinates;
- authorized resolver can recover exact semantic state;
- modified ciphertext fails authentication;
- wrong domain key cannot decrypt;
- stale epoch cannot silently override current epoch;
- sanitizer emits approved abstraction only;
- canonical hash mismatch fails closed;
- public export contains no private mapping;
- restart/handoff preserves authorized continuity;
- mapping rotation preserves provenance;
- access revocation prevents future resolution.

---

## 20. FAILURE MODES

Explicit failure classes include:

- semantic-map leakage;
- key leakage;
- cross-domain overexposure;
- visibility downgrade without authority;
- stale-epoch override;
- token collision;
- canonical-hash mismatch;
- public sanitizer bypass;
- unauthorized resolver access;
- relationship loss;
- restart inability;
- misleading obfuscation treated as encryption.

---

## 21. MERGE RECOMMENDATION

**Recommendation: MODIFY / MERGE → GOVERNANCE + BLUE STATE.**

Governance absorbs:
- classification;
- visibility;
- authority;
- retention;
- declassification;
- rotation;
- key-policy;
- public-boundary rules.

Blue State absorbs:
- protected semantic continuity;
- relationship preservation;
- restart/handoff recovery;
- epoch/version state persistence.

FORX owns:
- security enforcement;
- forensic verification;
- disclosure testing;
- leakage detection;
- remediation packets.

T-COD implements only after authorization.

---

## 22. ACCEPTANCE STATUS

**Owner acceptance:** YES.  
**Indexed candidate:** YES.  
**Merged:** NO.  
**Canon:** NO.  
**Build-authorized:** NO.  
**Black-box/top routing:** YES — via authoritative top-of-intake interpretation.  
**Governance destination:** YES.  
**Blue State destination:** YES.  
