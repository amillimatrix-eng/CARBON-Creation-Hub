import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.store import EvidenceStore


def write_repo(root: Path):
    (root/'evidence').mkdir(parents=True)
    (root/'overdrive').mkdir(parents=True)
    (root/'house/remediation').mkdir(parents=True)
    (root/'evidence/index.json').write_text(json.dumps({
        'records':[{
            'evidence_id':'EVID-TEST-001','capability':'Governed AI workflow','artifact':'receipt engine',
            'authoritative_source':'repo','status_freshness':'CURRENT','interview_safe_explanation':'Built durable evidence workflows.'
        }]
    }))
    (root/'overdrive/worker_contract.json').write_text(json.dumps({
        'status':'CONTROL_COMMISSIONED / PENDING_FIRST_POST_CORRECTION_ATTRIBUTABLE_EXECUTION_RECEIPT',
        'execution':{'decision_runtime':{'state':'ENABLED','acceptance_state':'PENDING_FIRST_POST_CORRECTION_ATTRIBUTABLE_EXECUTION_RECEIPT'}},
        'current_evidence':{'truth':'SCHEDULER_WOKE / POST-CORRECTION MATERIAL EXECUTION NOT PROVEN'},
        'acceptance_v2':{'state':'PENDING'}
    }))
    (root/'overdrive/opportunities.json').write_text(json.dumps({'records':{
        'a':{'organization':'A','state':'SUBMITTED','due_at':'2999-01-01T00:00:00Z','next_action':'wait'},
        'b':{'organization':'B','state':'QUALIFIED','next_action':'act'},
    }}))
    (root/'overdrive/signals.json').write_text(json.dumps({'PRI':[{'x':1}],'iSCOPE':[]}))
    (root/'overdrive/claims.json').write_text(json.dumps({'claims':{'b':{}},'ready_count':1}))
    (root/'overdrive/payment_rails.json').write_text(json.dumps({'inventory_completeness':'PARTIAL / RECOVERY_REQUIRED','rails':[{'provider':'PayPal'}]}))
    (root/'house/remediation/index.html').write_text('<html>house</html>')


def client(tmp_path):
    write_repo(tmp_path)
    return TestClient(create_app(tmp_path, tmp_path/'data/test.db'))


def test_health_and_seed_import(tmp_path):
    c=client(tmp_path)
    r=c.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='CONNECTED'
    e=c.get('/api/evidence/EVID-TEST-001'); assert e.status_code==200; assert e.json()['capability']=='Governed AI workflow'


def test_seed_import_is_idempotent(tmp_path):
    write_repo(tmp_path)
    store=EvidenceStore(tmp_path/'data/e.db')
    first=store.import_seed(tmp_path/'evidence/index.json')
    second=store.import_seed(tmp_path/'evidence/index.json')
    assert first['seen']==1
    assert second=={'seen':1,'inserted_or_updated':0}
    assert len(store.list())==1


def test_search_and_unsupported_gap(tmp_path):
    c=client(tmp_path)
    r=c.post('/api/evidence/search',json={'query':'governed workflow'}); assert r.status_code==200; assert r.json()['supported'] is True
    r=c.post('/api/evidence/search',json={'query':'quantum banana submarine'}); assert r.json()['supported'] is False; assert 'UNKNOWN/HOLD' in r.json()['gap']


def test_update_preserves_version_and_admin_fails_closed(tmp_path, monkeypatch):
    c=client(tmp_path)
    payload=c.get('/api/evidence/EVID-TEST-001').json(); payload['artifact']='changed artifact'
    r=c.put('/api/evidence/EVID-TEST-001',json=payload); assert r.status_code==503
    monkeypatch.setenv('AMX_ADMIN_TOKEN','secret')
    c=TestClient(create_app(tmp_path,tmp_path/'data/test.db'))
    r=c.put('/api/evidence/EVID-TEST-001',headers={'X-AMX-Admin':'secret'},json=payload); assert r.status_code==200; assert r.json()['changed'] is True
    versions=c.get('/api/evidence/EVID-TEST-001/versions').json(); assert versions['count']==1


def test_operator_truth_does_not_promote_enabled_to_executing(tmp_path):
    c=client(tmp_path)
    op=c.get('/api/operator/state').json()
    assert op['worker']['display_state']=='ENABLED / EXECUTION_NOT_PROVEN'
    assert op['worker']['runtime_enabled'] is True


def test_full_ledger_is_not_routing_subset(tmp_path):
    c=client(tmp_path)
    op=c.get('/api/operator/state').json()
    assert op['routing']['full_ledger_count']==2
    assert op['routing']['claim_count']==1
    assert op['routing']['invariant']=='FULL_LEDGER != ROUTING_SUBSET'


def test_payment_partial_is_preserved(tmp_path):
    c=client(tmp_path)
    op=c.get('/api/operator/state').json()
    assert op['payment_rails']['inventory_completeness']=='PARTIAL / RECOVERY_REQUIRED'


def test_no_paid_record_means_revenue_not_evidenced(tmp_path):
    c=client(tmp_path)
    op=c.get('/api/operator/state').json()
    assert op['opportunities']['realized_revenue_evidence']['present'] is False
    assert op['opportunities']['paid_record_count']==0


def test_invalid_evidence_rejected(tmp_path, monkeypatch):
    c=client(tmp_path); monkeypatch.setenv('AMX_ADMIN_TOKEN','secret')
    bad={'evidence_id':'BAD','capability':'','artifact':'x','authoritative_source':'repo','status_freshness':'CURRENT','interview_safe_explanation':'x'}
    r=c.put('/api/evidence/BAD',headers={'X-AMX-Admin':'secret'},json=bad)
    assert r.status_code==422


def test_house_bootstrap_and_static_house(tmp_path):
    c=client(tmp_path)
    b=c.get('/api/house/bootstrap'); assert b.status_code==200; assert b.json()['controls']['no_false_live_state'] is True
    h=c.get('/house'); assert h.status_code==200; assert 'house' in h.text
