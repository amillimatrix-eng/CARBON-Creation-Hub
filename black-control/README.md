# BLACK outbound execution bootstrap
Created 2026-09-30. Status: SOURCE COMMITTED; NOT INSTALLED OR RUNTIME VERIFIED.

## Connection
Fresh controller namespace `black-control/` in this repository.
Connected AMX tools write queue.json and read returned receipts/artifacts.
BLACK polls GitHub HTTPS from Ubuntu. No Watchtower, Opera, SSH, Tailscale, public port,
local model, paid service or extra ChatGPT automation slot is required for this adapter.
Repository is public: only public, non-sensitive jobs/artifacts belong here.
Private Matrix governance, account secrets, customer data and private media are excluded.
This is NOT an unrestricted remote terminal or full Matrix execution platform.

## First job
`black-package-manifest-20260930`: reads four fixed already-public package paths,
computes SHA-256 and returns JSON + HTML + terminal receipt.
Video access, external acceptance and payment remain UNVERIFIED.
Only adapter `package_manifest` exists. New capabilities require implemented adapters;
unsupported shell commands are rejected, not executed.
One enrolled BLACK instance. Linux flock prevents concurrent local instances.
Remote receipt creation uses GitHub compare-and-swap; completed task IDs are immutable.
RUNNING pure manifest tasks can resume after restart. FAILED requires diagnosis and a new job ID;
there is no automatic retry of completed FAILED tasks.

## Initial enrollment
One local Ubuntu installer run is unavoidable until some execution route exists.
Requires Python 3, curl, sudo and running systemd. Installer stops before enrollment
if systemd is absent; it does not install an OS or alter Windows.
A fine-grained GitHub token limited to this repository, Contents read/write, is entered
at a hidden LOCAL prompt and stored mode 0600. Never send that token through chat.
Existing ChatGPT GitHub credentials are not exportable to BLACK.
Installer pins worker source to commit 860c1c6d2affa9e8c7a1eaaafdfecca578c9b3a5.
Download pinned installer then run it:
```bash
curl -fL https://raw.githubusercontent.com/amillimatrix-eng/CARBON-Creation-Hub/64827822462af2fc88d0c3634b7b4331877b1812/black-control/bootstrap.sh -o /tmp/amx-black-bootstrap.sh && sudo bash /tmp/amx-black-bootstrap.sh
```
This code is untested at runtime in this conversation because the execution environment is unavailable.
Installer performs Python compilation on BLACK before service activation.
Service is CPU-limited to 25% and RAM-limited to 192 MB; limits need actual 2 GB-node validation.
No Windows boot/hibernation settings are modified.

## Remaining acceptance
1. Credential enrollment and installer execution on BLACK.
2. Receipt `black-control/receipts/black-package-manifest-20260930.json` = DONE.
3. Artifact hash checked and HTML/JSON opened.
4. Service restart and task deduplication verified.
5. Determine Ubuntu type and enable Windows-to-WSL auto-launch if applicable.
   Linux service startup does not by itself start WSL after Windows boot.
6. Integrate these records with existing House dashboard; not implemented by this bootstrap.
Until those receipts exist, do not mark BLACK commissioned.

## Operations
Linux: `systemctl status amx-black`, `journalctl -u amx-black`.
Stop: `sudo systemctl disable --now amx-black`.
No automatic code updates. Executor deployment requires explicit reviewed version.
Queue jobs are read from repository default branch via authenticated GitHub API.
Transport failures retry after 120 seconds. Normal poll 60 seconds.
No secrets, hostname or local filesystem contents are returned.
