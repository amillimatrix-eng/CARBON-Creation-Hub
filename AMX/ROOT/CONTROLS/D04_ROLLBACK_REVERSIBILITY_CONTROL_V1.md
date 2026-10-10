# D04 ROLLBACK / REVERSIBILITY CONTROL V1
Date: 2026-10-10
Control: CHG06

## Rule
Every consequential internal change must record:
1. pre-change source/commit or state snapshot;
2. change/issue/PR identifier;
3. whether the action is internally reversible or externally irreversible;
4. rollback authority and method;
5. tests/readback required after rollback;
6. residual effects that cannot be undone.

## Reversibility classes
- INTERNAL_REVERSIBLE: repository code/config, non-destructive projection data, internal documentation. Roll back through Git/state restoration and rerun the original acceptance condition.
- EXTERNAL_COMPENSATABLE: CRM projections or provider-side metadata that can be corrected but not literally erased from audit history. Correct and preserve the prior event.
- EXTERNAL_IRREVERSIBLE: sent email, submitted application, payment, buyer-visible action. Never call these "rolled back." Use a compensating action only when authorized and preserve both events.
- OWNER/PROVIDER_GATED: identity/KYC/auth/security action that cannot be reversed or executed by the worker without authority.

## Current application
PR #25 / issue #24:
- implementation is INTERNAL_REVERSIBLE via Git;
- external Gmail evidence ingested by the repair is not rolled back or deleted;
- rollback requires restoring pre-#25 code/state semantics, rerunning missing-record tests, then verifying canonical/provider truth is still preserved.

PR #26:
- semantic-no-op repair is INTERNAL_REVERSIBLE via Git;
- rollback acceptance requires rerunning the no-op wake test and observing the expected prior behavior only if an authorized rollback is intentionally performed.

## Prohibition
A rollback may never be used to erase evidence, rewrite historical execution, or pretend an externally visible action did not happen.
