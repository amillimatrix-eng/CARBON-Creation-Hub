#!/usr/bin/env python3
import json
from pathlib import Path

p = Path(__file__).with_name("matrix-required-state.json")
state = json.loads(p.read_text(encoding="utf-8"))
required = {"HOBO", "JAM3S", "IRIS", "CARBON"}
declared = set(state.get("required", []))

if declared != required:
    raise SystemExit("FAIL: required Matrix state is incomplete")

print("PASS: required Matrix state declared")
