# Security and secret-handling review

178 current files and all 350 commits reachable from tested branch commit
567c8c0737294da15c1dc16a7974eef9f02c217d were scanned without printing matches.
The 1,035 commit-message/text-file patch records extend to the initial commit on
2026-09-30; no requested commit or changed-file patch was missing. No credential
signature was found in that scope. This pattern-based review cannot prove the
absence of arbitrary unrecognized credential strings. The machine-readable
security receipt identifies the exact pinned history and scanner limitations.

Fixed: public BLACK command arrays lacked grants; remote queue synchronization
deployed code; public raw stdout/stderr could reveal secrets; private evidence
versions could leak via a public read endpoint; runtime/.env/database files lacked
ignore rules; validation workflow permissions were implicit; receipt IDs could
escape their directory. Root/Critic/Reaper learning API credentials are distinct,
promotion rejects the worker's credential and absent durable-storage acceptance.
Shared token values across Reaper, Critic or Root roles are also rejected, even
when environment variable names differ. Reinstallation preserves accepted grants,
registry and extra environment settings. Drive OAuth refresh is restricted to a
separate private credential directory; sealed key/policy directories stay
read-only in the service sandbox.

New secret boundaries: local recovery key, scoped read-only rclone configuration,
sealed grants and role tokens live outside Git with mode 0600. Ciphertext,
manifests, observations and recovery receipts are authenticated/encrypted. Recovery
key cannot reside under the ciphertext store or accompany a replica. Public health
is an explicit field allowlist. Subprocess arguments are arrays; source paths and
IDs are validated; credentials/exception bodies/worker stdout are not published.

Current deployed BLACK is still the historical worker until reviewed code/service
promotion. The new policy is not claimed as installed from source existence.
Actual installation needs a fresh service/config/source and restore receipt.
WSL service startup is separate from Windows login/boot. Existing Windows startup
provenance is preserved; no forced restart, duplicate unit or new remote shell.

No exposure requiring rotation was identified in inspected source/history. If a
new scan finds a real credential: preserve only source/line/hash/type evidence,
contain the exposed current file without deleting unrelated state, revoke/rotate
at the issuer, enroll the new scoped secret locally, then re-scan. Editing Git
history does not revoke a token; never reproduce its value in a remediation receipt.

Residual controls: GitHub write permission remains needed by the existing
OVERDRIVE job but is restricted to that job; main branch protection is not enabled
in the inspected repository. Review/promotion controls should be applied through
the existing repository owner/admin policy. No separate manager or dashboard is
introduced. Independent offline key escrow and ciphertext custody remain explicit
gates until their actual readback/restore receipt exists.
