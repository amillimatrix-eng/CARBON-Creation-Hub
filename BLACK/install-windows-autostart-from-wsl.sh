#!/usr/bin/env bash
set -euo pipefail

SERVICE="amx-black.service"
DISTRO="${AMX_BLACK_WSL_DISTRO:-Ubuntu}"
PRIMARY="/mnt/c/Users/eztra/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
STARTUP=""

if [ -d "$PRIMARY" ] && [ -w "$PRIMARY" ]; then
  STARTUP="$PRIMARY"
else
  while IFS= read -r p; do
    case "$p" in
      */Default/*|*/"Default User"/*|*/Public/*) continue ;;
    esac
    if [ -w "$p" ]; then STARTUP="$p"; break; fi
  done < <(find /mnt/c/Users -type d -path '*/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup' -print 2>/dev/null)
fi

if [ -z "$STARTUP" ]; then
  echo "BLACK_WINDOWS_STARTUP_WRITABLE_PATH_NOT_FOUND"
  exit 78
fi

LAUNCHER="$STARTUP/AMX-BLACK-WSL.cmd"
TMP="$LAUNCHER.tmp"
printf '%s\r\n'   '@echo off'   'REM AMilliMATRiX BLACK - wake WSL and start the existing supervised worker'   "wsl.exe -d \"$DISTRO\" -u root --exec /bin/systemctl start $SERVICE >NUL 2>&1"   > "$TMP"
mv -f "$TMP" "$LAUNCHER"

echo "BLACK_WINDOWS_STARTUP_BRIDGE_INSTALLED"
echo "launcher=$LAUNCHER"
echo "distro=$DISTRO"
echo "service=$SERVICE"
echo "launcher_sha256=$(sha256sum "$LAUNCHER" | awk '{print $1}')"
echo "linux_service_enabled=$(systemctl is-enabled "$SERVICE" 2>/dev/null || true)"
echo "linux_service_active=$(systemctl is-active "$SERVICE" 2>/dev/null || true)"
