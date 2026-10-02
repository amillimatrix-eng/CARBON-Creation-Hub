#!/usr/bin/env bash
set -e
cd "$HOME"
if [ ! -d amx-black/.git ]; then gh repo clone amillimatrix-eng/CARBON-Creation-Hub amx-black; fi
cd amx-black
git config user.name "AMX BLACK"
git config user.email "amillimatrix@gmail.com"
mkdir -p BLACK/jobs BLACK/receipts
nohup python3 BLACK/worker.py > "$HOME/black.log" 2>&1 &
echo $! > "$HOME/black.pid"
echo "BLACK ONLINE pid=$(cat "$HOME/black.pid")"
