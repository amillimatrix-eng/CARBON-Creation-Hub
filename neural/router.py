from __future__ import annotations
import json, math, os, time
from pathlib import Path
from typing import Any

DEFAULT_WEIGHTS = {
  "revenue": 3.0, "probability": 2.4, "urgency": 1.4, "evidence": 1.8,
  "latency": -0.8, "dependency_risk": -2.2, "cost": -1.0, "blocked": -8.0
}

class NeuralRouter:
    def __init__(self, state_path: Path, weights: dict[str,float] | None=None):
        self.state_path=state_path; self.weights=dict(DEFAULT_WEIGHTS); self.weights.update(weights or {})
        self.state=self._load()
    def _load(self):
        if self.state_path.exists(): return json.loads(self.state_path.read_text(encoding="utf-8"))
        return {"schema":"AMX_NEURAL_ROUTER_V1","observations":0,"executors":{},"last_routes":[]}
    def _save(self):
        self.state_path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.state_path.with_suffix(".tmp"); tmp.write_text(json.dumps(self.state,indent=2,sort_keys=True),encoding="utf-8"); tmp.replace(self.state_path)
    def score(self, x: dict[str,Any]):
        s=sum(self.weights.get(k,0.0)*float(x.get(k,0) or 0) for k in self.weights)
        hist=self.state["executors"].get(str(x.get("name")),{})
        s += 2.0*float(hist.get("success_rate",0.5))-0.35*float(hist.get("mean_latency_s",0.0))/60.0
        return round(s,6)
    def route(self, objective: dict[str,Any], executors: list[dict[str,Any]]):
        viable=[e for e in executors if e.get("available",False) and objective.get("capability") in e.get("capabilities",[])]
        if not viable: return {"state":"UNKNOWN_HOLD","reason":"NO_AUTHORIZED_AVAILABLE_EXECUTOR"}
        ranked=sorted([dict(e,score=self.score(e)) for e in viable],key=lambda e:e["score"],reverse=True)
        decision={"state":"ROUTED","objective_id":objective["objective_id"],"selected":ranked[0]["name"],"ranked":ranked,"ts":time.time()}
        self.state["last_routes"]=(self.state.get("last_routes",[])+[decision])[-100:]; self._save(); return decision
    def learn(self, executor: str, success: bool, latency_s: float):
        e=self.state["executors"].setdefault(executor,{"runs":0,"wins":0,"mean_latency_s":0.0,"success_rate":0.5})
        e["runs"]+=1; e["wins"]+=int(success); n=e["runs"]; e["mean_latency_s"]=((n-1)*e["mean_latency_s"]+latency_s)/n; e["success_rate"]=e["wins"]/n
        self.state["observations"]=self.state.get("observations",0)+1; self._save(); return e

def exercise(root: Path):
    router=NeuralRouter(root/"data/neural_router_state.json")
    objective={"objective_id":"NEURAL-PROOF-001","capability":"python-local-static","revenue":1}
    executors=[{"name":"BLACK","available":False,"capabilities":["python-local-static"],"blocked":1,"dependency_risk":1},
               {"name":"RENDER","available":True,"capabilities":["python-local-static"],"revenue":1,"probability":1,"evidence":1,"latency":0.2},
               {"name":"GITHUB","available":True,"capabilities":["durable-state"],"evidence":1}]
    d=router.route(objective,executors)
    ok=d.get("selected")=="RENDER"; router.learn(d.get("selected","NONE"),ok,0.01)
    return {"pass":ok,"decision":d,"state":router.state}