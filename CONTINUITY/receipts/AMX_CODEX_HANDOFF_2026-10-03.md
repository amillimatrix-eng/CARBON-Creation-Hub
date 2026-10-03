# AMX durable commissioning handoff

**State: HOLD. The terminal directive remains open.**

Repository: amillimatrix-eng/CARBON-Creation-Hub
Branch: codex/amx-continuity-security-20261003
Tested implementation: 567c8c0737294da15c1dc16a7974eef9f02c217d
Review: https://github.com/amillimatrix-eng/CARBON-Creation-Hub/pull/7

Implemented within existing BLACK, backend/EvidenceStore, OVERDRIVE, worker registry and House: encrypted versioned recovery, registry/Drive inventory, isolated restoration, immutable receipts, scoped grants, hardened services/timer, private evidence protection, asset eligibility and governed Reaper learning. No duplicate worker, Matrix or dashboard.

Verification: 54 tests passed, including 37 control-plane tests; HTTP smoke, systemd unit validation, reinstallation preservation and container runtime passed. Encrypted clean-target restoration compared 207 registered files. Current-source and all 350 reachable commits (1,035 message/file patch records) were scanned with no credential signature findings. All 40 implementation blobs were read back without mismatch.

CI: https://github.com/amillimatrix-eng/CARBON-Creation-Hub/actions/runs/37140021542

| Acceptance | State | Scope |
| --- | --- | --- |
| A_REPOSITORY | PASS | Clean GitHub checkout, declared dependencies, 54 tests, HTTP smoke, service-unit validation, container build/runtime. All 40 implementation blobs read back with matching Git hashes. |
| B_BLACK | HOLD | Existing service was read back once; three later command preflights timed out. New hardened installation/timer/encrypted live restore and complete boot path are not proved. |
| C_DRIVE_LOSS | HOLD | Private governed Drive estate has no enrolled BLACK read-only OAuth/inventory/mirror receipt. |
| D_INTEGRITY | PASS | Deliberate chunk/manifest corruption, wrong key, tampered receipt/truncation, and failed required source cannot silently replace accepted recovery state. |
| E_RESTORE | PASS | 207 registered repository files reconstructed and compared in clean CI; new temporary targets; no live authority overwritten. Private estate remains outside tested scope. |
| F_SECRETS | PASS | No credential signatures found; .env/runtime ignores, private-version access, least grants, secret permissions and distinct role bindings verified. |
| G_WORKER_LEARNING | PASS | Existing Reaper source evidence audit -> outcome -> receipt -> hypothesis -> bounded candidate -> Critic tests -> Root version-CAS promotion. Worker token, shared role bindings and untested/mandate changes rejected. |
| H_BOUNTY_REAPER | PASS | Existing independent crypto bounty/reward mandate preserved; source normalization improves duplicate filtering; original package custody limitation retained. No submission, accepted bounty or payout inferred. |
| I_NO_DUPLICATION | PASS | Existing BLACK, EvidenceStore, OVERDRIVE routing adapter, worker registry and House/API extended. No second Matrix/Root/PRI/iSCOPE/Reaper/CARBON/House/dashboard. |

Remaining dependency actions are prepared in [RUNBOOK.md](../RUNBOOK.md):

- BLACK_SERVICE_PROMOTION: On BLACK, inspect existing amx-black.service and its private journal, test bounded native command execution, then install the read-back reviewed source with sudo bash BLACK/install-continuity.sh. Do not infer privilege loss from timeout receipts or reset the node blindly. Resume: Existing worker and 30-minute continuity timer run bounded sync, verification and isolated restoration without repeated Owner relay.
- DRIVE_READ_ENROLLMENT: Install rclone from the trusted node package channel. Configure one scoped drive.readonly remote in /var/lib/amx-black-credentials/rclone.conf (0600); set AMX_DRIVE_DISCOVERY_REMOTE in the preserved private environment. Root accepts classification/authority through existing governance, never by provider identity. Resume: periodic stable-ID inventory/export/mirror; missing sources retained
- INDEPENDENT_CUSTODY: Enroll replica and escrow once; prove restore from them Resume: bounded ciphertext retention/verification; no new approval per sync
- WINDOWS_NO_TOUCH_BOOT: Existing launcher wakes WSL; obtain fresh autonomous BLACK receipt after that boot Resume: Linux system service/timer runs without Owner relay
- LEARNING_RUNTIME_DURABILITY: Bind the existing EvidenceStore to accepted persistent storage; prove reopen/backup/restore. Set distinct AMX_REAPER_TOKEN, AMX_CRITIC_TOKEN and AMX_ROOT_TOKEN only on their authorized services. Enable AMX_LEARNING_DURABLE_STORAGE only after that proof. Do not enable mutation on ephemeral free Render. Resume: Reaper outcomes and Critic/Root tested version promotion

BLACK readback: first service/WSL preflight exited 0; three later install/user/native preflights exited 124. Their historical RESOLVED labels do not prove command success. Receipt transport works; later execution is DEGRADED/UNKNOWN. New encryption installation, Drive estate recovery, independent disk/key custody and complete Windows -> WSL -> Linux boot remain unproved.

A real local existing-Reaper evidence audit and candidate test/promotion passed; live bounty execution, submissions and payouts were not claimed. Worker package custody and live durability remain explicit constraints.

Exact changed files, hashes, CI artifact provenance and acceptance evidence are in AMX_CODEX_HANDOFF_2026-10-03.json. Earlier receipts remain preserved with their original scope. This receipt commit follows the tested code commit; its SHA is reported after publication/readback.

Receipt SHA-256: f63bc890166e63c674a9bc1585c10210e7e36ae9472c354297a6a1b6047f56dd
