# ROOT RECONCILIATION — ISSUE #8 MONEY-HOME REMEDIATION

Date: 2026-10-05
Authority: Root Librarian reconciliation
Source directive: GitHub issue #8 — CODEX DIRECTIVE — Lean Egg Security + Revenue Run
Merged PR: #9
Merge SHA: 7708b782eb7cd96f0b05ae58e7c2091d7a2e735f
State: MERGED / SOURCE-VALIDATED / RUNTIME DEPLOYMENT NOT YET VERIFIED
Egg truth: EGG NOT BROKEN — NO VERIFIED PAYMENT EVIDENCE

## Verified durable facts

1. PR #9 is CLOSED + MERGED into main at merge SHA `7708b782eb7cd96f0b05ae58e7c2091d7a2e735f`.
2. The remediation folder exists at:
   `AMX/ROOT/INTAKE/RUN_OUTCOMES/CODEX_ISSUE_8_REMEDIATION/`
3. `VALIDATION.json` records:
   - 41 targeted tests PASS;
   - changed Python parse PASS across 9 files;
   - smoke PASS;
   - diff check PASS;
   - implementation worktree CLEAN;
   - deployment = NOT_VERIFIED;
   - verified_payment_evidence = [];
   - EGG NOT BROKEN.
4. Payment truth is fail-closed in `overdrive/payment_truth.py`: internal labels, invoices, email and arbitrary receipts do not establish PAID; settlement must be independently verified, inbound, attributable and matched to opportunity/payer/payee/currency/amount.
5. BLACK receipt truth is corrected in `BLACK/worker.py`: failed and timed-out jobs are no longer reported as RESOLVED; retries are opt-in, bounded and attributable; historical failure receipts are preserved.
6. Privacy/intake remediation is merged: deny-by-default/private control surfaces, proposal registry removed from published repository state, customer requests deduped and associated to existing PRI ownership.
7. Commercial routing remains role-preserving: iSCOPE pre-handoff, PRI post-handoff, iSCOPE PRI Field Force sole commercial writer, OVERDRIVE transport/evidence. No duplicate commercial executor was introduced.

## Not yet proven / not closed

- BLACK is not yet proven to be running the merged worker code.
- Public-host/backend deployment of the merged remediation is not yet verified.
- Private runtime proposal registry/intake storage provisioning is not yet verified.
- Independent payment-verifier key/runtime provisioning is not yet verified.
- No real customer-request progression through the newly secured private intake path is yet evidenced.
- No verified incoming payment exists.

## Root disposition

KEEP ISSUE #8 OPEN AS DEPLOYMENT/PROVISIONING FOLLOW-THROUGH.

Do not replay the broad Codex remediation sweep. Do not reopen the code fixes without contrary evidence.
Progress only the remaining runtime/deployment dependencies, while preserving commercial execution and the EGG objective.

T10:
- Supposed outcome: remove false PAID, false BLACK success, private exposure and commercial HOLD/READY ambiguity without redesigning the Matrix.
- Actual outcome: code remediation merged and source validation passed.
- Proof: PR #9, merge SHA above, remediation README, VALIDATION.json, merged source.
- Changed: source/control behavior.
- Still unproven: deployed runtime behavior, private provisioning, real customer-request progression, realized payment.
