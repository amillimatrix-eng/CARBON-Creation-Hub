#!/usr/bin/env python3
import json,subprocess,time,pathlib,datetime,sys,os,hashlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
JOBS=ROOT/"BLACK"/"jobs"
RCPT=ROOT/"BLACK"/"receipts"
SELF=pathlib.Path(__file__).resolve()
JOBS.mkdir(parents=True,exist_ok=True)
RCPT.mkdir(parents=True,exist_ok=True)
os.environ["PATH"]=f"{pathlib.Path.home()}/.local/bin:"+os.environ.get("PATH","")

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def log(msg): print(f"{now()} {msg}",file=sys.stderr,flush=True)
def sh(a,timeout=120):
 try:
  q=subprocess.run(a,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
 except subprocess.TimeoutExpired as e:
  out=e.stdout.decode(errors="replace") if isinstance(e.stdout,bytes) else (e.stdout or "")
  err=e.stderr.decode(errors="replace") if isinstance(e.stderr,bytes) else (e.stderr or "")
  err += f"\nAMX_OUTER_TIMEOUT after {timeout}s"
  log(f"CMD_TIMEOUT timeout={timeout}s cmd={a!r}")
  return type("R",(),{"returncode":124,"stdout":out,"stderr":err})()
 if q.returncode: log(f"CMD_FAIL rc={q.returncode} cmd={a!r} stderr={q.stderr[-2000:]!r}")
 return q

def self_hash():
 try: return hashlib.sha256(SELF.read_bytes()).hexdigest()
 except Exception: return ""

def sync_control_plane():
 before=self_hash()
 q=sh(["git","fetch","origin","main"],60)
 if q.returncode: return False
 q=sh(["git","rebase","origin/main"],90)
 if q.returncode:
  sh(["git","rebase","--abort"],20)
  log("CONTROL_SYNC_REBASE_FAILED")
  return False
 q=sh(["git","push","origin","HEAD:main"],60)
 if q.returncode:
  q=sh(["git","fetch","origin","main"],60)
  if q.returncode: return False
  q=sh(["git","rebase","origin/main"],90)
  if q.returncode:
   sh(["git","rebase","--abort"],20)
   return False
  q=sh(["git","push","origin","HEAD:main"],60)
  if q.returncode: return False
 after=self_hash()
 if before and after and before!=after:
  log("WORKER_CODE_UPDATED_REEXEC")
  os.execv(sys.executable,[sys.executable,str(SELF)])
 return True

while True:
 try:
  if not sync_control_plane():
   time.sleep(10); continue
  for p in sorted(JOBS.glob("*.json")):
   rid=p.stem
   if (RCPT/f"{rid}.json").exists(): continue
   try:
    j=json.loads(p.read_text()); cmd=j.get("command")
    if not isinstance(cmd,list) or not cmd:
     log(f"JOB_INVALID {rid}"); continue
    limit=max(1,int(j.get("timeout",120)))
    started=now(); log(f"JOB_START {rid}")
    wrapped=["timeout","--signal=TERM","--kill-after=3s",f"{limit}s"]+[str(x) for x in cmd]
    q=sh(wrapped,limit+8)
    rec={"job":rid,"worker":"BLACK","state":"RESOLVED","exit_code":q.returncode,"started":started,"finished":now(),"stdout":q.stdout[-12000:],"stderr":q.stderr[-12000:]}
    out=RCPT/f"{rid}.json"; out.write_text(json.dumps(rec,indent=2)+"\n")
    if sh(["git","add",str(out.relative_to(ROOT))],30).returncode: continue
    if sh(["git","commit","-m",f"BLACK receipt {rid}"],30).returncode: continue
    push=sh(["git","push","origin","HEAD:main"],60)
    if push.returncode: log(f"RECEIPT_PUSH_PENDING {rid}")
    else: log(f"JOB_RECEIPT_PUSHED {rid}")
   except Exception as e:
    log(f"JOB_LOOP_ERROR {rid} {e!r}")
 except Exception as e:
  log(f"WORKER_LOOP_ERROR {e!r}")
 time.sleep(10)
