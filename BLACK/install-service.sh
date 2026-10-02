#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT="$HOME/.config/systemd/user/amx-black.service"
mkdir -p "$(dirname "$UNIT")"
cat > "$UNIT" <<EOF
[Unit]
Description=AMilliMATRiX BLACK Worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$ROOT
ExecStart=/usr/bin/python3 $ROOT/BLACK/worker.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable amx-black.service
# replace bootstrap/nohup worker with supervised instance
if [ -f "$HOME/black.pid" ]; then kill "$(cat "$HOME/black.pid")" 2>/dev/null || true; fi
systemctl --user restart amx-black.service
systemctl --user is-enabled amx-black.service
systemctl --user is-active amx-black.service
