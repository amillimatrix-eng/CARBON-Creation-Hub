#!/usr/bin/env python3
import json,subprocess,time,pathlib,datetime,sys,os,hashlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
JOBS=ROOT/"BLACK"/"jobs"
RCPT=ROOT/"BLACK"/"receipts"
SELF=pathlib.Path(__file__).resolve()

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
 except OSError as e:
  return type("R",(),{"returncode":127,"stdout":"","stderr":f"AMX_COMMAND_START_FAILED {type(e).__name__}"})()
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

def process_job(p):
 rid=p.stem
 j=json.loads(p.read_text()); cmd=j.get("command")
 if not isinstance(cmd,list) or not cmd:
  raise ValueError(f"JOB_INVALID {rid}")
 instructions={k:v for k,v in j.items() if k not in {"max_attempts","retry_delay_seconds"}}
 task_hash=hashlib.sha256(json.dumps(instructions,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 paths=[RCPT/f"{rid}.json"]+sorted(RCPT.glob(f"{rid}.attempt-*.json"))
 prior=[]
 for path in paths:
  if not path.exists(): continue
  rec=json.loads(path.read_text())
  if rec.get("task_sha256") and rec["task_sha256"]!=task_hash:
   raise ValueError(f"JOB_CHANGED {rid}: use a new job ID")
  if rec.get("exit_code")==0 and rec.get("state") in {"RESOLVED","SUCCEEDED"}:
   return None
  prior.append((path,rec))
 # Opt in to retrying potentially non-idempotent historical shell jobs.
 maximum=max(1,min(3,int(j.get("max_attempts",1))))
 if len(prior)>=maximum: return None
 if prior:
  finished=datetime.datetime.fromisoformat(prior[-1][1]["finished"].replace("Z","+00:00"))
  delay=max(10,min(3600,int(j.get("retry_delay_seconds",60))))
  if datetime.datetime.now(datetime.timezone.utc)-finished < datetime.timedelta(seconds=delay): return None
 attempt=len(prior)+1
 limit=max(1,int(j.get("timeout",120)))
 started=now(); log(f"JOB_START {rid} attempt={attempt}")
 wrapped=["timeout","--signal=TERM","--kill-after=3s",f"{limit}s"]+[str(x) for x in cmd]
 q=sh(wrapped,limit+8)
 state="SUCCEEDED" if q.returncode==0 else ("TIMED_OUT" if q.returncode in {124,137} else "FAILED")
 rec={"job":rid,"worker":"BLACK","state":state,"exit_code":q.returncode,"attempt":attempt,
      "task_sha256":task_hash,"started":started,"finished":now(),"stdout":q.stdout[-12000:],"stderr":q.stderr[-12000:]}
 if prior:
  previous=prior[-1][0]
  rec.update(previous_receipt=previous.name,previous_receipt_sha256=hashlib.sha256(previous.read_bytes()).hexdigest())
 out=RCPT/(f"{rid}.json" if attempt==1 else f"{rid}.attempt-{attempt:03d}.json")
 # Immutable attempts; the historical receipt is never replaced.
 with out.open("x") as handle: handle.write(json.dumps(rec,indent=2)+"\n")
 if sh(["git","add",str(out.relative_to(ROOT))],30).returncode: return rec
 if sh(["git","commit","-m",f"BLACK receipt {rid} attempt {attempt}: {state}"],30).returncode: return rec
 push=sh(["git","push","origin","HEAD:main"],60)
 log(f"RECEIPT_PUSH_PENDING {rid}" if push.returncode else f"JOB_RECEIPT_PUSHED {rid}")
 return rec

def main():
 JOBS.mkdir(parents=True,exist_ok=True)
 RCPT.mkdir(parents=True,exist_ok=True)
 os.environ["PATH"]=f"{pathlib.Path.home()}/.local/bin:"+os.environ.get("PATH","")
 while True:
  try:
   if not sync_control_plane():
    time.sleep(10); continue
   for p in sorted(JOBS.glob("*.json")):
    try: process_job(p)
    except Exception as e: log(f"JOB_LOOP_ERROR {p.stem} {e!r}")
  except Exception as e: log(f"WORKER_LOOP_ERROR {e!r}")
  time.sleep(10)

if __name__=="__main__": main()
