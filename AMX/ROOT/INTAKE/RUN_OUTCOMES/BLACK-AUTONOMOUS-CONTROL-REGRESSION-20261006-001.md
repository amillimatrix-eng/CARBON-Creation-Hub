# AMX RUN OUTCOME — BLACK AUTONOMOUS CONTROL REGRESSION

RUN_ID: BLACK-AUTONOMOUS-CONTROL-REGRESSION-20261006-001
DATE: 2026-10-06
TARGET: BLACK physical WSL worker
STATE: DEGRADED — SOURCE REMEDIATION MERGED / PHYSICAL ACTIVATION UNPROVEN
AUTHORITY: Root recovery under existing BLACK / Issue #8 execution scope
LIFECYCLE: EVIDENCE / RUN OUTCOME — NOT CANON

## Trigger

Matrix-side acceptance job is present on main but BLACK has not consumed it and no durable receipt exists.

Acceptance canary:
- job: BLACK-RECEIPT-VERIFY-20261006-1140-001
- queue commit: ae8f0d6ef0746400facf802af7e5c4bc23045d44
- required receipt: BLACK/receipts/BLACK-RECEIPT-VERIFY-20261006-1140-001.json
- readback at remediation time: NOT FOUND

NO RECEIPT -> NO CLOSURE.

## Recovered evidence

1. Last proven fresh BLACK autonomous receipts were emitted on 2026-10-04, including:
   - BLACK-AUTONOMY-RECOVERY-20261004
   - BLACK-CODEX-READINESS-20261004
2. The current BLACK worker performed:
   fetch origin/main -> rebase origin/main -> push origin HEAD:main
   before reading BLACK/jobs.
3. Therefore write-transport failure could block read-side queue intake entirely.
4. The Oct 4 Codex startup outcome also records a prior stale Git index.lock fault on the shared BLACK clone.
5. BLACK local/Codex activity and worker control-plane Git operations share /home/amx/amx-black, so a dirty worktree or Git lock can likewise block the pre-job rebase.
6. Existing repository recovery utility BLACK/repair-live.sh already preserves local state, repairs divergence and restarts amx-black.service. It requires execution on the physical host.
7. No commissioned SSH/Tailscale/public-port/self-hosted-runner remote host control was recovered. The earlier black-control adapter is explicitly uncommissioned and is not substituted as a second transport.
8. BullRulez currently has repository pull permission but not push permission. This is a possible credential-migration risk only; the active BLACK credential identity is not proven from the connected control surface and must not be inferred.

## Source remediation executed

PR #10:
BLACK: decouple queue intake from receipt publication

Repair commit:
c37f4cac1424dc3dd1c0404c97c961b409e04ddd

Merge to main:
57fd11cded791a23cfa06ed0fd61229e9235e24c

Resulting behavior:
- fetch/rebase is the queue-intake gate;
- receipt push is no longer a prerequisite for job execution;
- local receipt evidence is preserved if publication is degraded;
- receipt publication retries independently each loop;
- worker self-update is evaluated immediately after successful read synchronization.

No second worker, queue or transport was introduced.

Static validation before merge:
- worker.py compiled successfully;
- regression check confirmed no git push remains in sync_control_plane();
- PR contained one changed file only and was mergeable.

## Post-merge acceptance readback

Existing canary receipt:
BLACK/receipts/BLACK-RECEIPT-VERIFY-20261006-1140-001.json

Result:
NOT FOUND.

Therefore source repair is merged but runtime recovery is NOT proven.

## Remaining activation gate

The currently running physical worker may still be executing pre-repair code, or may be blocked before updating its worktree by a dirty clone / Git lock / fetch transport failure.

The existing governed local recovery mechanism is:
BLACK/repair-live.sh

When an authorized execution surface can reach the physical BLACK host, use the existing recovery mechanism to preserve local state, synchronize the clone and restart amx-black.service. Do not create a replacement BLACK transport merely to bypass this gate.

This dependency remains ACTIVE and must resurface automatically when a host-capable control surface becomes available. It is not routed to the Owner as ordinary terminal work.

## Closure condition

BLACK returns a fresh durable receipt for:
BLACK-RECEIPT-VERIFY-20261006-1140-001

The receipt must be read back from GitHub and prove exit_code 0 / successful execution.

Until then:

BLACK DEGRADED — AUTONOMOUS CONTROL REGRESSION OPEN.
NO RECEIPT -> NO CLOSURE.
