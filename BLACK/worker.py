#!/usr/bin/env python3
import json,subprocess,time,pathlib,datetime,hashlib,os
ROOT=pathlib.Path(__file__).resolve().parents[1]; JOBS=ROOT/"BLACK"/"jobs"; RCPT=ROOT/"BLACK"/"receipts"
JOBS.mkdir(parents=True,exist_ok=True); RCPT.mkdir(parents=True,exist_ok=True)
def sh(a,timeout=120): return subprocess.run(a,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
while True:
 try:
  sh(["git","pull","--ff-only"],60)
  for p in sorted(JOBS.glob("*.json")):
   rid=p.stem
   if (RCPT/f"{rid}.json").exists(): continue
   j=json.loads(p.read_text()); cmd=j.get("command")
   if not isinstance(cmd,list) or not cmd: continue
   started=datetime.datetime.now(datetime.timezone.utc).isoformat()
   try:
    q=sh([str(x) for x in cmd],int(j.get("timeout",120)))
    rec={"job":rid,"worker":"BLACK","state":"RESOLVED","exit_code":q.returncode,"started":started,"finished":datetime.datetime.now(datetime.timezone.utc).isoformat(),"stdout":q.stdout[-12000:],"stderr":q.stderr[-12000:]}
   except Exception as e:
    rec={"job":rid,"worker":"BLACK","state":"RESOLVED","exit_code":-1,"started":started,"finished":datetime.datetime.now(datetime.timezone.utc).isoformat(),"error":repr(e)}
   out=RCPT/f"{rid}.json"; out.write_text(json.dumps(rec,indent=2)+"\n")
   sh(["git","add",str(out.relative_to(ROOT))]); sh(["git","commit","-m",f"BLACK receipt {rid}"]); sh(["git","push"],60)
 except Exception: pass
 time.sleep(10)
