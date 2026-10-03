#!/usr/bin/env python3
"""Existing BLACK executor: fixed adapters, sealed grants, immutable receipts.

Queue synchronization never deploys code. Code promotion uses the installation
runbook. Legacy commands remain a capability on HOLD until explicitly scoped.
"""
from __future__ import annotations
import base64
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.continuity import atomic, canonical, digest, git_version, now
from backend.security import authorized_job, authorize, fingerprint, local_grants

REPO = "amillimatrix-eng/CARBON-Creation-Hub"
JOB_ID = re.compile(r"^[A-Za-z0-9_-]{1,100}$")


def safe_run(argv, timeout=60):
    try:
        return subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(argv, 124, b"", b"")
    except OSError:
        return subprocess.CompletedProcess(argv, 127, b"", b"")


def sync_control_plane():
    # Fetch transport only. Do not rebase/re-exec remotely changed production code.
    result = safe_run(["git", "fetch", "origin", "main"], 60)
    return result.returncode == 0


def execute(job, authorization):
    adapter = authorization["adapter"]
    if adapter != "scoped_command":
        from BLACK.continuity import operation
        action = {"continuity_sync":"sync","continuity_verify":"verify",
                  "continuity_restore_test":"restore-test","continuity_health":"health"}[adapter]
        result = operation(action)
        return {"exit_code":0 if result.get("state")=="PASS" else 2,"result":result}
    limit = max(1, min(600, int(job.get("timeout",120))))
    result = safe_run(["timeout","--signal=TERM","--kill-after=3s",str(limit)+"s",*job["command"]], limit+8)
    return {"exit_code":result.returncode,
            "stdout_sha256":digest(result.stdout), "stderr_sha256":digest(result.stderr),
            "raw_output_retained_or_published":False}


def publish(receipt):
    name = receipt["job"]+"--attempt-"+str(receipt["attempt"]).zfill(4)+".json"
    route = "repos/"+REPO+"/contents/BLACK/receipts/"+name
    old = safe_run(["gh","api",route],30)
    if old.returncode == 0:
        try:
            prior = json.loads(base64.b64decode(json.loads(old.stdout)["content"]))
            return prior == receipt
        except (ValueError, KeyError):
            return False
    # Only a confirmed 404 permits create; transient failures must not overwrite.
    if b"404" not in old.stderr:
        return False
    body = {"message":"BLACK scoped receipt "+receipt["job"],
            "content":base64.b64encode(canonical(receipt)+b"\n").decode()}
    with tempfile.NamedTemporaryFile(mode="wb") as f:
        f.write(canonical(body)); f.flush()
        return safe_run(["gh","api","--method","PUT",route,"--input",f.name,"--silent"],30).returncode == 0


class Worker:
    def __init__(self, state_root=None, grants=None, executor=execute, publisher=publish):
        self.state = Path(state_root or os.environ.get("AMX_BLACK_STATE_ROOT",Path.home()/".local/state/amx-black")).absolute()
        if self.state.is_symlink() or ROOT in self.state.parents:
            raise ValueError("PRIVATE_RUNTIME_OUTSIDE_GIT_REQUIRED")
        self.state.mkdir(parents=True,exist_ok=True,mode=0o700)
        if self.state.stat().st_mode & 0o077:
            raise PermissionError("BLACK_STATE_PERMISSIONS")
        for name in ["journal","outbox"]:
            (self.state/name).mkdir(exist_ok=True,mode=0o700)
        self.grants = grants if grants is not None else local_grants(ROOT)
        self.executor, self.publisher = executor, publisher

    def process(self, jid, job):
        if not JOB_ID.fullmatch(jid):
            raise ValueError("INVALID_JOB_ID")
        job_hash = fingerprint(job)
        journal = self.state/"journal"/(jid+".json")
        old = json.loads(journal.read_text()) if journal.exists() else None
        if old and old["job_sha256"] != job_hash:
            raise ValueError("JOB_ID_CONFLICT_HOLD")
        if old and old["state"] in {"RESOLVED","FAILED"}:
            return old
        if old and old["state"] == "RUNNING" and old["adapter"] == "scoped_command":
            receipt = {**old,"state":"HOLD","reason":"INTERRUPTED_CONSEQUENTIAL_COMMAND_REQUIRES_RECONCILIATION","finished":now()}
            atomic(journal,canonical(receipt))
            name = jid+"--attempt-"+str(receipt["attempt"]).zfill(4)+".json"
            atomic(self.state/"outbox"/name,canonical(receipt),immutable=True)
            return receipt
        if old and old.get("reason") == "INTERRUPTED_CONSEQUENTIAL_COMMAND_REQUIRES_RECONCILIATION":
            return old
        if old and old["state"] == "HOLD" and time.time()-old.get("retry_clock",0)<60:
            return old
        attempt = old.get("attempt",0)+1 if old else 1
        receipt = {"schema":"AMX.BLACK.SCOPED_RECEIPT.v1","job":jid,"worker":"BLACK",
                   "job_sha256":job_hash,"attempt":attempt,"started":now(),
                   "source_version":git_version(ROOT),"config_sha256":fingerprint(self.grants)}
        try:
            authorization = authorized_job(job,self.grants)
            receipt.update(adapter=authorization["adapter"],grant_id=authorization["grant_id"],state="RUNNING")
            atomic(journal,canonical(receipt))
            result = self.executor(job,authorization)
            receipt.update(result)
            receipt["state"] = "RESOLVED" if result["exit_code"] == 0 else ("HOLD" if authorization["adapter"] != "scoped_command" else "FAILED")
        except PermissionError:
            receipt.update(state="HOLD",reason="CAPABILITY_GRANT_REQUIRED",
                           command_sha256=fingerprint(job.get("command",[])),
                           remediation="Seal a narrow exact-argv grant locally; do not grant through the public queue.")
        except Exception as exc:
            receipt.update(state="HOLD",reason="DEPENDENCY_OR_EXECUTION_REVIEW",error_type=type(exc).__name__)
        receipt.update(finished=now(),retry_clock=time.time(),payout_state="UNPROVEN")
        atomic(journal,canonical(receipt))
        name = jid+"--attempt-"+str(attempt).zfill(4)+".json"
        atomic(self.state/"outbox"/name,canonical(receipt),immutable=True)
        return receipt

    def flush_outbox(self):
        authorize(self.grants,"BLACK","write_receipts","black-jobs")
        authorize(self.grants,"BLACK","access_network","github-queue-and-receipts")
        sent=0
        for path in sorted((self.state/"outbox").glob("*.json")):
            receipt=json.loads(path.read_text())
            if self.publisher(receipt):
                path.unlink(); sent+=1
        return sent


def cycle(worker):
    authorize(worker.grants,"BLACK","read_governance","github-public-jobqueue")
    authorize(worker.grants,"BLACK","access_network","github-queue-and-receipts")
    worker.flush_outbox()  # retry publication even when queue transport is unavailable
    if not sync_control_plane():
        return {"state":"HOLD","reason":"QUEUE_PROVIDER_UNAVAILABLE","existing_capability_preserved":True}
    paths = safe_run(["git","ls-tree","-r","--name-only","origin/main","--","BLACK/jobs/"])
    if paths.returncode:
        return {"state":"HOLD","reason":"QUEUE_READ_FAILED"}
    count=0
    for raw in paths.stdout.decode().splitlines():
        p=Path(raw); jid=p.stem
        if p.suffix != ".json" or not JOB_ID.fullmatch(jid):
            continue
        legacy=safe_run(["git","show","origin/main:BLACK/receipts/"+jid+".json"])
        if legacy.returncode == 0:
            # Preserve historic receipts and failed jobs; no blind replay on deployment.
            continue
        result=safe_run(["git","show","origin/main:"+raw])
        if result.returncode:
            continue
        try:
            worker.process(jid,json.loads(result.stdout)); count+=1
        except (ValueError,TypeError):
            continue
    worker.flush_outbox()
    return {"state":"QUEUE_READBACK","jobs_checked":count,"source_version":git_version(ROOT),
            "material_execution_not_inferred":True}


def main():
    worker=Worker()
    fd=os.open(worker.state/"worker.lock",os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"a") as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        while True:
            try:
                result=cycle(worker)
                atomic(worker.state/"worker-health.json",canonical({**result,"at":now()}))
                print(json.dumps(result,sort_keys=True),flush=True)
            except Exception as exc:
                print(json.dumps({"state":"HOLD","error_type":type(exc).__name__}),flush=True)
            if "--once" in sys.argv:
                return 0
            time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
