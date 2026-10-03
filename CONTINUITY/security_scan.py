#!/usr/bin/env python3
"""Redacted current/history secret detection. Never print matches or raw patches."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "openai_token": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b"),
    "aws_access_id": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "google_api_key": re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "credential_assignment": re.compile(r"(?im)(?:api[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[:=]\s*[\"']([A-Za-z0-9+/=_-]{24,})[\"']"),
}


def scan_text(text: str, source: str) -> list[dict]:
    findings = []
    for kind, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            value = match.group(0)
            # Documentary placeholders and generated test pattern text are not credentials.
            if any(x in value.lower() for x in ["replace-with", "example", "placeholder"]):
                continue
            findings.append({"source": source, "kind": kind,
                "line": text.count("\n", 0, match.start())+1,
                "evidence_sha256": hashlib.sha256(value.encode()).hexdigest(),
                "secret_value": "REDACTED", "state": "ROTATION_REVIEW_REQUIRED"})
    return findings


def run(history_patches: Path | None = None) -> dict:
    files = subprocess.run(["git","ls-files","-z","--cached","--others","--exclude-standard"],cwd=ROOT,capture_output=True,check=True).stdout
    paths = sorted({p.decode() for p in files.split(b"\0") if p})
    findings=[]
    for name in paths:
        path=ROOT/name
        if path.is_file() and not path.is_symlink():
            findings.extend(scan_text(path.read_text(errors="replace"), name))
    log = subprocess.run(["git","log","--all","--format=%H","--max-count=10000"],cwd=ROOT,capture_output=True,check=True,text=True).stdout.splitlines()
    for commit in log:
        patches=subprocess.run(["git","show","--format=fuller","--no-ext-diff",commit],cwd=ROOT,capture_output=True,check=True,text=True).stdout
        findings.extend(scan_text(patches,"git-history:"+commit))
    remote_count=0
    if history_patches:
        items=json.loads(history_patches.read_text())
        for item in items:
            remote_count+=1
            findings.extend(scan_text(item.get("patch",""),"remote-history:"+item["commit"]+":"+item["path"]))
    return {"schema":"AMX.SECURITY.REVIEW.v1","state":"PASS" if not findings else "HOLD",
        "files_scanned":len(paths),"local_commits_scanned":len(log),"remote_file_patches_scanned":remote_count,
        "history_scope":"Available local commits and supplied remote patches; older uninspected history remains explicit HOLD",
        "findings":findings,"raw_secrets_disclosed":False,
        "rotation_action":"If an actual production credential is identified, revoke/rotate at its issuer, replace the scoped local binding, remove exposed current material and re-scan; a commit deletion does not revoke a credential."}


def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--history-patches",type=Path);args=p.parse_args()
    result=run(args.history_patches);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ["state","files_scanned","local_commits_scanned","remote_file_patches_scanned","raw_secrets_disclosed"]}))
    return 0 if result["state"]=="PASS" else 2


if __name__=="__main__":
    raise SystemExit(main())
