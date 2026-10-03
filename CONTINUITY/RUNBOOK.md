# Installation, migration and recovery

Use the existing BLACK account/node and repository. Do not run legacy
black-control/bootstrap.sh or create a second worker. Deployment source must be
the read-back reviewed branch/commit, not an unpinned HTTP installer.

Local dependency/test commands:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python CONTINUITY/commission.py --output /tmp/amx-commissioning
python CONTINUITY/security_scan.py --output /tmp/amx-security.json
bash BLACK/install-continuity.sh --stage /tmp/amx-service-stage
```

On existing BLACK, after source promotion under existing authority:

```bash
sudo bash BLACK/install-continuity.sh
systemctl is-active amx-black.service
systemctl is-enabled amx-black-continuity.timer
```

The installer preserves an enrolled key/private registry, installs one system
BLACK service and one operation timer, retires only the obsolete duplicate user
unit, pins grants/registry/source and creates a 0600 local key without displaying
it. Reinstallation preserves enrolled policy, registry and extra environment settings.
Keys and sealed config remain under /etc/amx-black-continuity; refreshable Drive
credentials use /var/lib/amx-black-credentials with private service-only access.
Ciphertext remains under
/var/lib/amx-black-continuity, worker journal/outbox under /var/lib/amx-black.
If administrative access is unavailable, all source/tests/staged units remain
reviewable and the precise live-install gate remains HOLD.

Drive refresh dependency: install rclone through the node's trusted signed package
channel. Configure **one scoped read-only Drive remote**, on BLACK locally, in
/var/lib/amx-black-credentials/rclone.conf. Use drive.readonly and only the authorized
Matrix folder/source estate. Do not transfer ChatGPT connector tokens or paste
OAuth material into chat. Legitimate account consent is a provider gate; subsequent
refreshes do not require human attention. Set AMX_DRIVE_DISCOVERY_REMOTE=amx_drive:
in the private environment file to enable automatic inventory and native exports.
Existing classifications are retained; new unclassified references await Root's
normal evidence intake. Missing provider entries are never treated as deletion.

Manual registry edits must be governed and repinned by the installer; a public
queue cannot expand sources, command grants, credentials or production permissions.
The installer also preserves a previously sealed grants file. Add only reviewed
new scopes to that existing file and rerun the installer to repin it; never replace
accepted command grants with a default policy. The refreshable Drive credential
directory is writable only for the scoped BLACK services; key/policy directories
remain read-only in the service sandbox.
Legacy shell access requires an exact argv digest in a sealed local grant. Typed
sync/verify/restore-test jobs accept no arbitrary target, source URL or shell text.

```bash
sudo -u amx bash -c 'set -a; . /etc/amx-black-continuity/environment; set +a; python3 /home/amx/amx-black/BLACK/continuity.py sync'
sudo -u amx bash -c 'set -a; . /etc/amx-black-continuity/environment; set +a; python3 /home/amx/amx-black/BLACK/continuity.py restore-test'
```

Restore accepts a **new** target outside the live repository/store. It verifies
manifest, chunks, file hashes, reconstructs privately, compares and writes an
encrypted PASS/FAIL receipt. The marker retains authority metadata and declares
MIRROR_RECOVERY; no copied file becomes Canon. To inspect an older generation use
the verified snapshot ID and `restore --snapshot ID --target NEW_PRIVATE_TARGET`.
Corruption is evidence, not permission to overwrite an accepted generation.

Replication uses `replicate --target NEW_DIRECTORY_ON_INDEPENDENT_DEVICE` and
refuses same-device disaster-recovery claims. It copies ciphertext only. Escrow
the key separately through the existing authorized secret-custody mechanism and
prove decryption/restoration from independent custody. Never commit the key or
include it with the ciphertext. Retention preserves at least seven generations,
30 days, active snapshot and the last restore-tested snapshot.

Learning uses the existing EvidenceStore and Reaper adapter. Set separate Root,
Critic and Reaper tokens only in the services needing each token. Enable accepted
durable learning storage only after volume/backup/reopen/restore evidence exists;
the current free Render runtime cannot supply that acceptance by a config label.
Workers can record evidence/lessons/candidates. Critic runs bounded tests; Root
performs version-CAS promotion/rejection/rollback. No worker can grant itself a
mandate, deploy, submit externally, spend, sign or infer payment through learning.

Rollback: preserve ciphertext/receipts; stop only the continuity timer if required;
restore prior reviewed code/service and sealed config; retain failed candidate and
capability versions. Never delete the working Matrix or reset newer source state.

Windows/WSL: preserve the installed Windows launcher. Linux is-enabled/is-active
and timer enablement do not prove Windows boot. On the next natural Windows login
or reboot, require a fresh autonomous source/config/boot-correlated BLACK receipt.
No manual login/reinstallation is required merely to repeat historical acceptance.

Current live gate (2026-10-03): three bounded preflights produced exit 124 without
command readback. Restore the existing BLACK command-execution path before live
installation. A receipt labeled RESOLVED with nonzero exit status is not acceptance.
Do not infer missing privileges from those timeouts or reset the node blindly.
Once that path responds, the installer, OAuth enrollment, independent custody and
durability checks above are the resumable steps; routine sync/restore testing uses
the existing service timer and needs no repeated confirmation.
