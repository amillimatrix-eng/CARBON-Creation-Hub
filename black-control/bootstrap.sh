#!/usr/bin/env bash
# Run inside existing Ubuntu; no OS replacement, browser dependency or open ports.
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then
  echo "Run this installer with sudo."; exit 1
fi
BLACK_USER="${SUDO_USER:-}"
if [ -z "$BLACK_USER" ] || [ "$BLACK_USER" = root ]; then
  echo "Launch from your normal Ubuntu user with sudo."; exit 1
fi
command -v python3 >/dev/null || { echo "Python 3 is required."; exit 1; }
command -v curl >/dev/null || { echo "curl is required."; exit 1; }
if ! [ -d /run/systemd/system ]; then
  echo "This Ubuntu session has no running systemd. Nothing installed."
  echo "WSL startup integration must be prepared for this environment before enrollment."
  exit 1
fi
BLACK_USER_HOME="$(getent passwd "$BLACK_USER" | cut -d: -f6)"
BLACK_DIR="$BLACK_USER_HOME/.local/share/amx-black"
BLACK_TMP="$(mktemp -d)"
trap 'rm -rf "$BLACK_TMP"' EXIT
curl --fail --silent --show-error --location \
  https://raw.githubusercontent.com/amillimatrix-eng/CARBON-Creation-Hub/860c1c6d2affa9e8c7a1eaaafdfecca578c9b3a5/black-control/worker.py \
  -o "$BLACK_TMP/worker.py"
python3 -m py_compile "$BLACK_TMP/worker.py"
install -d -m 755 /opt/amx-black
install -m 644 "$BLACK_TMP/worker.py" /opt/amx-black/worker.py
install -d -m 700 -o "$BLACK_USER" -g "$(id -gn "$BLACK_USER")" "$BLACK_DIR"
# Credential is entered locally, never sent through chat or published.
if ! [ -s "$BLACK_DIR/token" ]; then
  BLACK_TOKEN_PATH="$BLACK_DIR/token" python3 - <<'PY'
import getpass, os
path = os.environ["BLACK_TOKEN_PATH"]
token = getpass.getpass("GitHub fine-grained token (only CARBON-Creation-Hub; Contents read/write): ").strip()
if not token:
    raise SystemExit("Enrollment cancelled: no token")
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as f:
    f.write(token + "\n")
PY
  chown "$BLACK_USER:$(id -gn "$BLACK_USER")" "$BLACK_DIR/token"
fi
cat > /etc/systemd/system/amx-black.service <<EOF
[Unit]
Description=AMX BLACK outbound worker
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
User=$BLACK_USER
Environment=BLACK_HOME=$BLACK_DIR
ExecStart=/usr/bin/python3 /opt/amx-black/worker.py
Restart=on-failure
RestartSec=30
MemoryMax=192M
CPUQuota=25%
Nice=10
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$BLACK_DIR
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now amx-black.service
echo "Worker service started. Installation is NOT task acceptance."
echo "Verify black-control/receipts/black-package-manifest-20260930.json in GitHub."
if grep -qi microsoft /proc/sys/kernel/osrelease; then
  echo "WSL detected: this service starts with Ubuntu, not by itself when Windows boots."
  echo "Windows-to-WSL automatic launch and restart recovery remain UNVERIFIED."
fi
