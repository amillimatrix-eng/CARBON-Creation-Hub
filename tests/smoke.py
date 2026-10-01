import json, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app import create_app

root=Path(__file__).resolve().parents[1]
app=create_app(root, Path(tempfile.mkdtemp())/'smoke.db')
c=TestClient(app)
assert c.get('/api/health').status_code==200
assert c.get('/api/house/bootstrap').status_code==200
q=c.post('/api/evidence/search',json={'query':'workflow evidence','limit':5})
assert q.status_code==200
assert c.get('/house').status_code==200
print(json.dumps({'health':'PASS','bootstrap':'PASS','evidence_search':'PASS','house':'PASS','result_count':q.json()['count']}))
