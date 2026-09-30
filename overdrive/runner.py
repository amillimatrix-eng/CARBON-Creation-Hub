#!/usr/bin/env python3
import json, os, sys, time, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
STATE=ROOT/"state.json"; LOCK=ROOT/".tick.lock"; RECEIPTS=ROOT/"receipts"
RECEIPTS.mkdir(exist_ok=True)

def now(): return datetime.now(timezone.utc).isoformat()
def load(): return json.loads(STATE.read_text())
def save(s): STATE.write_text(json.dumps(s,indent=2)+"\n")
def lock():
    if LOCK.exists() and time.time()-LOCK.stat().st_mtime < 110: return False
    LOCK.write_text(str(os.getpid())); return True
def receipt(payload):
    raw=json.dumps(payload,sort_keys=True).encode()
    payload["sha256"]=hashlib.sha256(raw).hexdigest()
    p=RECEIPTS/f'{payload["sequence"]:010d}.json'
    p.write_text(json.dumps(payload,indent=2)+"\n")
    return p
def tick():
    if not lock():
        print("OVERDRIVE HOLD: active tick"); return 0
    try:
        s=load(); s["sequence"]+=1; s["last_tick"]=now()
        work=[]
        for lane,data in s["lanes"].items():
            if data.get("state")=="ACTIVE":
                work.append({"lane":lane,"action":"RESUME_FURTHEST_EVIDENCED_STATE","result":"READY_FOR_ADAPTER"})
        r={"sequence":s["sequence"],"ts":s["last_tick"],"work":work,"queue_depth":len(s.get("queue",[]))}
        p=receipt(r); s["last_receipt"]=str(p.relative_to(ROOT)); save(s)
        print(json.dumps(r)); return 0
    finally:
        LOCK.unlink(missing_ok=True)
if __name__=="__main__":
    if len(sys.argv)<2 or sys.argv[1]!="tick": raise SystemExit("usage: runner.py tick")
    raise SystemExit(tick())
