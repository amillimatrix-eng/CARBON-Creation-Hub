#!/usr/bin/env python3
import json, hashlib, os, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
P=ROOT/"AMX_MATRIX_MANIFEST_V1.json"
m=json.loads(P.read_text(encoding="utf-8"))
required={"HOBO","JAM3S","IRIS","CARBON"}
errors=[]
ecos=m.get("ecosystems",{})
if set(ecos)!=required:
    errors.append("ECOSYSTEM_SET_MISMATCH")
for name in sorted(required):
    e=ecos.get(name,{})
    for field in ("identity","purpose","custody","state"):
        if not e.get(field): errors.append(f"{name}:{field}:MISSING")
    c=e.get("custody",{})
    if not c.get("repo") or not c.get("head"): errors.append(f"{name}:REPO_HEAD_MISSING")

# Optional live source recovery. With GITHUB_TOKEN, private BullRulez sources are verified
# against exact recorded heads. Without it, authority remains candidate-only.
live={}
token=os.getenv("GITHUB_TOKEN")
if token:
    for name,e in ecos.items():
        repo=e["custody"]["repo"]; expected=e["custody"]["head"]
        req=urllib.request.Request(f"https://api.github.com/repos/{repo}/commits/{expected}",
            headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req,timeout=20) as resp:
                data=json.load(resp)
            live[name]="PASS" if data.get("sha")==expected else "FAIL"
        except Exception as ex:
            live[name]=f"FAIL:{type(ex).__name__}"
            errors.append(f"{name}:LIVE_SOURCE_RECOVERY_FAIL")
else:
    live={n:"NOT_RUN_NO_GITHUB_TOKEN" for n in required}

manifest_sha=hashlib.sha256(P.read_bytes()).hexdigest()
receipt={
 "schema":"AMX_MATRIX_RECONSTRUCTION_RECEIPT_V1",
 "manifest_sha256":manifest_sha,
 "required_ecosystems":sorted(required),
 "structural_falsification":"PASS" if not [e for e in errors if "LIVE_SOURCE" not in e] else "FAIL",
 "live_source_recovery":live,
 "unresolved_preserved":{
   "HOBO":"current runtime/deployment UNKNOWN_HOLD",
   "JAM3S":"James-Bot/JAM3S_BOT/package code-level lineage HOLD",
   "IRIS":"current editable/runtime source gap UNKNOWN_HOLD",
   "CARBON":"complete authoritative child-pillar inventory UNKNOWN_HOLD"
 },
 "authority":"ROOT_ACTIVE_ONLY_AFTER_RUNTIME_SOURCE_RECOVERY_PASS" if token and not errors else "CANDIDATE_NO_NEW_AUTHORITY",
 "errors":errors
}
out=ROOT/"AMX_MATRIX_RECONSTRUCTION_RECEIPT_LATEST.json"
out.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
print(json.dumps(receipt,indent=2))
raise SystemExit(1 if errors else 0)
