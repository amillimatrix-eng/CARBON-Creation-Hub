# D04 SECURITY RECOVERY TABLETOP — 2026-10-10
Control: SEC08
Type: non-destructive tabletop; no credentials exposed and no destructive action performed.

## Scenario A — connector credential/provider compromise
Signal: unexpected provider write/send, permission change, impossible receipt, or unauthorized state mutation.
Contain:
1. stop only the affected connector/execution lane;
2. preserve provider IDs/logs and canonical pre-event state;
3. do not disable unrelated Matrix lanes.
Recover:
1. rotate/revoke credential through Owner/provider authority where required;
2. switch to tested alternate read/write route if available;
3. reconcile provider action against canonical ledger;
4. re-run original acceptance/readback.
Verify:
- credential/permission state is known;
- no unauthorized lifecycle promotion remains;
- affected canonical record and provider receipt reconcile.
Owner-only gate: credential/KYC/security challenge requiring account holder.

## Scenario B — private evidence leakage into public surface
Signal: controlled PII/payroll/bank/identity material appears in public/canonical output beyond the minimum proof boundary.
Contain:
1. stop further propagation;
2. preserve a restricted incident reference, not additional copies;
3. revoke public exposure using provider controls if authorized.
Recover:
1. replace public artifact with hash/source-bound public-safe claim;
2. preserve governed provenance that a redaction/replacement occurred;
3. inspect downstream mirrors/caches where controllable.
Verify:
- public artifact no longer contains the sensitive material;
- canonical claim remains evidence-bound;
- no secrets/OTP/passwords were persisted.

## Acceptance
PASS for tabletop coverage: detection → containment → alternate/recovery route → verification → Owner/external gate are all explicitly exercised on two realistic scenarios. This is not evidence of a real breach.
