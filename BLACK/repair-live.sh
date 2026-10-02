#!/usr/bin/env bash
set -euo pipefail

REPO=/home/amx/amx-black
SERVICE=amx-black.service
STAMP=$(date -u +%Y%m%dT%H%M%SZ)

if [ "$(id -u)" -ne 0 ]; then
  echo "BLACK_RECOVERY_REQUIRES_ROOT"
  exit 77
fi
if [ ! -d "$REPO/.git" ]; then
  echo "BLACK_REPO_NOT_FOUND=$REPO"
  exit 78
fi

echo "===BLACK_RECOVERY_START==="
echo "utc=$STAMP"

# Stop the worker so repository repair and worker writes cannot race.
systemctl stop "$SERVICE" || true

# Preserve all local state before synchronization.
runuser -u amx -- bash -lc "
  set -euo pipefail
  cd '$REPO'
  git branch 'black-recovery-$STAMP' HEAD
  if [ -n \"$(git status --porcelain)\" ]; then
    git stash push -u -m 'BLACK recovery $STAMP'
  fi
  git fetch origin main
  if git merge-base --is-ancestor HEAD origin/main; then
    git merge --ff-only origin/main
  elif git merge-base --is-ancestor origin/main HEAD; then
    git push origin HEAD:main
  else
    git rebase origin/main
    git push origin HEAD:main
  fi
  git status --short
  git rev-parse HEAD
"

systemctl daemon-reload
systemctl restart "$SERVICE"
sleep 3

echo "===BLACK_SERVICE==="
systemctl is-enabled "$SERVICE" || true
systemctl is-active "$SERVICE"
systemctl show "$SERVICE" -p User -p MainPID -p ActiveState -p SubState --no-pager

echo "===BLACK_RECENT_LOG==="
journalctl -u "$SERVICE" -n 60 --no-pager || true

echo "===BLACK_RECOVERY_COMPLETE==="
