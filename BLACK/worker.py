#!/usr/bin/env python3
import json,subprocess,time,pathlib,datetime,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; JOBS=ROOT/"BLACK"/"jobs"; RCPT=ROOT/"BLACK"/"receipts"
JOBS.mkdir(parents=True,exist_ok=True); RCPT.mkdir(parents=True,exist_ok=True)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def log(msg): print(f"{now()} {msg}",file=sys.stderr,flush=True)
def sh(a,timeout=120):
 q=subprocess.run(a,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
 if q.returncode: log(f"CMD_FAIL rc={q.returncode} cmd={a!r} stderr={q.stderr[-2000:]!r}")
 return q
while True:
 try:
  pull=sh(["git","pull","--ff-only"],60)
  if pull.returncode:
   time.sleep(10); continue
  for p in sorted(JOBS.glob("*.json")):
   rid=p.stem
   if (RCPT/f"{rid}.json").exists(): continue
   try:
    j=json.loads(p.read_text()); cmd=j.get("command")
    if not isinstance(cmd,list) or not cmd:
     log(f"JOB_INVALID {rid}"); continue
    started=now(); log(f"JOB_START {rid}")
    try:
     q=sh([str(x) for x in cmd],int(j.get("timeout",120)))
     rec={"job":rid,"worker":"BLACK","state":"RESOLVED","exit_code":q.returncode,"started":started,"finished":now(),"stdout":q.stdout[-12000:],"stderr":q.stderr[-12000:]}
    except Exception as e:
     rec={"job":rid,"worker":"BLACK","state":"RESOLVED","exit_code":-1,"started":started,"finished":now(),"error":repr(e)}
    out=RCPT/f"{rid}.json"; out.write_text(json.dumps(rec,indent=2)+"\n")
    sh(["git","add",str(out.relative_to(ROOT))])
    commit=sh(["git","commit","-m",f"BLACK receipt {rid}"])
    if commit.returncode: continue
    push=sh(["git","push"],60)
    if push.returncode: log(f"RECEIPT_PUSH_PENDING {rid}")
    else: log(f"JOB_RECEIPT_PUSHED {rid}")
   except Exception as e: log(f"JOB_LOOP_ERROR {rid} {e!r}")
 except Exception as e: log(f"WORKER_LOOP_ERROR {e!r}")
 time.sleep(10)
