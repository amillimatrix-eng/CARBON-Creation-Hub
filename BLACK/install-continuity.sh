#!/usr/bin/env bash
# Extend the installed BLACK node; --stage verifies generated configuration without activation.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
STAGE=""
if [[ "${1:-}" == "--stage" ]]; then STAGE="${2:?stage target required}"; fi
if [[ -z "$STAGE" && "$(id -u)" != 0 ]]; then echo 'HOLD: existing BLACK administrator required'; exit 77; fi
if [[ "$REPO" == *' '* || "$REPO" == *$'\n'* ]]; then echo 'HOLD: unsupported systemd source path'; exit 78; fi
if [[ -z "$STAGE" ]]; then
  id amx >/dev/null
  [[ "$(ps -p 1 -o comm=)" == systemd ]] || { echo 'HOLD: Linux systemd is not PID 1'; exit 78; }
  # Protect the deployed source: this installer never fetches/merges remote code.
  [[ -z "$(git -C "$REPO" status --porcelain)" ]] || { echo 'HOLD: deployed source must be clean'; exit 78; }
  python3 -c 'import cryptography,jsonschema'
fi
UNIT_DIR="${STAGE}/etc/systemd/system"
CONFIG_DIR="${STAGE}/etc/amx-black-continuity"
STATE_DIR="${STAGE}/var/lib/amx-black-continuity"
WORKER_STATE="${STAGE}/var/lib/amx-black"
CREDENTIAL_DIR="${STAGE}/var/lib/amx-black-credentials"
mkdir -p "$UNIT_DIR" "$CONFIG_DIR" "$STATE_DIR" "$WORKER_STATE" "$CREDENTIAL_DIR"
chmod 700 "$CONFIG_DIR" "$STATE_DIR" "$WORKER_STATE" "$CREDENTIAL_DIR"
# Preserve accepted local command grants; policy updates require governed repinning.
if [[ ! -f "$CONFIG_DIR/grants.json" ]]; then
  install -m 600 "$REPO/CONTINUITY/capability-grants.json" "$CONFIG_DIR/grants.json"
fi
if [[ -f "$CONFIG_DIR/rclone.conf" && ! -f "$CREDENTIAL_DIR/rclone.conf" ]]; then
  install -m 600 "$CONFIG_DIR/rclone.conf" "$CREDENTIAL_DIR/rclone.conf"
fi
# Preserve an already enrolled private registry and key on reinstallation.
if [[ ! -f "$CONFIG_DIR/source-registry.json" ]]; then
  install -m 600 "$REPO/CONTINUITY/source-registry.json" "$CONFIG_DIR/source-registry.json"
fi
POLICY_HASH="$(sha256sum "$CONFIG_DIR/grants.json" | cut -d ' ' -f 1)"
REGISTRY_HASH="$(sha256sum "$CONFIG_DIR/source-registry.json" | cut -d ' ' -f 1)"
SOURCE_COMMIT="$(git -C "$REPO" rev-parse HEAD)"
python3 - "$CONFIG_DIR/environment" "$POLICY_HASH" "$REGISTRY_HASH" "$SOURCE_COMMIT" <<'PY'
import os, sys, tempfile
from pathlib import Path
path = Path(sys.argv[1])
managed = '''
AMX_CONTINUITY_ROOT=/var/lib/amx-black-continuity
AMX_CONTINUITY_KEY_FILE=/etc/amx-black-continuity/recovery.key
AMX_SOURCE_REGISTRY=/etc/amx-black-continuity/source-registry.json
AMX_RCLONE_CONFIG_FILE=/var/lib/amx-black-credentials/rclone.conf
BLACK_GRANTS_FILE=/etc/amx-black-continuity/grants.json
AMX_BLACK_STATE_ROOT=/var/lib/amx-black
'''.strip().splitlines()
managed += ["BLACK_GRANTS_SHA256="+sys.argv[2], "AMX_SOURCE_REGISTRY_SHA256="+sys.argv[3],
            "AMX_INSTALLED_SOURCE_COMMIT="+sys.argv[4]]
names = {line.split('=', 1)[0] for line in managed}
prior = path.read_text().splitlines() if path.exists() else []
preserved = [line for line in prior if line.split('=', 1)[0].strip() not in names]
fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.environment-')
try:
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write('\n'.join(preserved+managed)+'\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
finally:
    Path(temporary).unlink(missing_ok=True)
PY
cat > "$UNIT_DIR/amx-black-continuity.service" <<EOF
[Unit]
Description=AMilliMATRiX BLACK encrypted continuity operation
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=amx
Group=amx
WorkingDirectory=$REPO
EnvironmentFile=/etc/amx-black-continuity/environment
ExecStart=/usr/bin/python3 $REPO/BLACK/continuity.py sync
TimeoutStartSec=20min
UMask=0077
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/lib/amx-black-continuity /var/lib/amx-black-credentials
RestrictSUIDSGID=yes
LockPersonality=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
MemoryMax=512M
CPUQuota=50%
EOF
cat > "$UNIT_DIR/amx-black-continuity.timer" <<'EOF'
[Unit]
Description=Periodic verified recovery on existing BLACK

[Timer]
OnBootSec=2min
OnUnitInactiveSec=30min
Persistent=true
RandomizedDelaySec=60
Unit=amx-black-continuity.service

[Install]
WantedBy=timers.target
EOF
cat > "$UNIT_DIR/amx-black.service" <<EOF
[Unit]
Description=AMilliMATRiX existing BLACK scoped worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=amx
Group=amx
WorkingDirectory=$REPO
EnvironmentFile=/etc/amx-black-continuity/environment
ExecStart=/usr/bin/python3 $REPO/BLACK/worker.py
Restart=on-failure
RestartSec=10
UMask=0077
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/lib/amx-black /var/lib/amx-black-continuity /var/lib/amx-black-credentials $REPO/.git
RestrictSUIDSGID=yes
LockPersonality=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
MemoryMax=512M

[Install]
WantedBy=multi-user.target
EOF
if [[ -n "$STAGE" ]]; then
  echo "STAGED: Linux worker/service/timer; live installation and Windows boot remain HOLD"
  exit 0
fi
chown -R amx:amx "$CONFIG_DIR" "$STATE_DIR" "$WORKER_STATE" "$CREDENTIAL_DIR"
if [[ ! -f "$CONFIG_DIR/recovery.key" ]]; then
  runuser -u amx -- /usr/bin/python3 "$REPO/BLACK/continuity.py" init-key --target "$CONFIG_DIR/recovery.key"
fi
# The existing system service is authoritative. Do not enroll historical black-control.
# Retire only the obsolete duplicate user unit, preserving it as local provenance.
LEGACY_UNIT=/home/amx/.config/systemd/user/amx-black.service
if [[ -f "$LEGACY_UNIT" ]]; then
  runuser -u amx -- systemctl --user disable --now amx-black.service || true
  mv "$LEGACY_UNIT" "$LEGACY_UNIT.superseded-$(date -u +%Y%m%dT%H%M%SZ)"
fi
systemctl daemon-reload
systemctl enable --now amx-black.service amx-black-continuity.timer
systemctl restart amx-black.service
systemctl is-active amx-black.service
systemctl is-enabled amx-black-continuity.timer
echo 'INSTALLED: verify fresh receipts; Drive enrollment and offline key escrow must be resolved locally'
