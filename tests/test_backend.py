import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.store import EvidenceStore
from backend.state import StateReader


def evidence_record(**overrides):
    record = {
        'evidence_id':'EVID-TEST-001',
        'capability':'Governed AI workflow',
        'artifact':'receipt engine',
        'authoritative_source':'repo',
        'status_freshness':'CURRENT',
        'interview_safe_explanation':'Built durable evidence workflows.',
        'T10_JOB':'Prove the governed workflow outcome.',
        'T10_ACTUAL':'A durable evidence record was written.',
        'T10_EVIDENCE':'repo::receipt',
        'T10_CHANGE':'The outcome became inspectable.',
        'T10_REMAINING_GAP':'No additional gap asserted for this fixture.',
        'T10_PASS':'PASS',
        'visibility':'HOUSE',
    }
    record.update(overrides)
    return record


def write_repo(root: Path):
    (root/'evidence').mkdir(parents=True)
    (root/'overdrive').mkdir(parents=True)
    (root/'house/remediation').mkdir(parents=True)
    (root/'CONTINUITY').mkdir(parents=True)
    (root/'evidence/index.json').write_text(json.dumps({'records':[evidence_record()]}))
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
    (root/'CONTINUITY/MATRIX_TRUTH_SCREEN.json').write_text(json.dumps({'schema':'AMX_MATRIX_TRUTH_SCREEN_V1','workers':[],'surfaces':[],'alerts':[]}))
    (root/'house/remediation/index.html').write_text('<html>house</html>')


def client(tmp_path):
    write_repo(tmp_path)
    return TestClient(create_app(tmp_path, tmp_path/'data/test.db'))


def test_health_and_seed_import(tmp_path):
    c=client(tmp_path)
    r=c.get('/api/health')
    assert r.status_code==200
    assert r.json()['status']=='CONNECTED'
    assert r.json()['schema_version']==2
    assert r.json()['t10']['coverage']['coverage_complete'] is True
    e=c.get('/api/evidence/EVID-TEST-001')
    assert e.status_code==200
    assert e.json()['capability']=='Governed AI workflow'
    assert e.json()['T10_PASS']=='PASS'


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
    r=c.post('/api/evidence/search',json={'query':'governed workflow'})
    assert r.status_code==200
    assert r.json()['supported'] is True
    r=c.post('/api/evidence/search',json={'query':'quantum banana submarine'})
    assert r.json()['supported'] is False
    assert 'UNKNOWN/HOLD' in r.json()['gap']


def test_update_preserves_version_and_admin_fails_closed(tmp_path, monkeypatch):
    c=client(tmp_path)
    payload=c.get('/api/evidence/EVID-TEST-001').json()
    payload['artifact']='changed artifact'
    r=c.put('/api/evidence/EVID-TEST-001',json=payload)
    assert r.status_code==503
    monkeypatch.setenv('AMX_ADMIN_TOKEN','secret')
    c=TestClient(create_app(tmp_path,tmp_path/'data/test.db'))
    r=c.put('/api/evidence/EVID-TEST-001',headers={'X-AMX-Admin':'secret'},json=payload)
    assert r.status_code==200
    assert r.json()['changed'] is True
    versions=c.get('/api/evidence/EVID-TEST-001/versions',headers={'X-AMX-Admin':'secret'}).json()
    assert versions['count']==1


def test_operator_truth_does_not_promote_enabled_to_executing(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "operator-test")
    c=client(tmp_path)
    c.headers["X-AMX-Admin"]="operator-test"
    op=c.get('/api/operator/state').json()
    assert op['worker']['display_state']=='ENABLED / EXECUTION_NOT_PROVEN'
    assert op['worker']['runtime_enabled'] is True
    assert op['worker']['t10']['T10_PASS']=='HOLD'


def test_full_ledger_is_not_routing_subset(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "operator-test")
    c=client(tmp_path)
    c.headers["X-AMX-Admin"]="operator-test"
    op=c.get('/api/operator/state').json()
    assert op['routing']['full_ledger_count']==2
    assert op['routing']['claim_count']==1
    assert op['routing']['invariant']=='FULL_LEDGER != ROUTING_SUBSET'
    assert op['routing']['t10']['T10_PASS']=='PASS'


def test_payment_partial_is_preserved_and_t10_hold(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "operator-test")
    c=client(tmp_path)
    c.headers["X-AMX-Admin"]="operator-test"
    op=c.get('/api/operator/state').json()
    assert op['payment_rails']['inventory_completeness']=='PARTIAL / RECOVERY_REQUIRED'
    assert op['payment_rails']['t10']['T10_PASS']=='HOLD'


def test_no_paid_record_means_revenue_not_evidenced(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "operator-test")
    c=client(tmp_path)
    c.headers["X-AMX-Admin"]="operator-test"
    op=c.get('/api/operator/state').json()
    assert op['opportunities']['realized_revenue_evidence']['present'] is False
    assert op['opportunities']['paid_record_count']==0


def test_t10_fields_are_required_for_new_evidence(tmp_path, monkeypatch):
    c=client(tmp_path)
    monkeypatch.setenv('AMX_ADMIN_TOKEN','secret')
    c=TestClient(create_app(tmp_path,tmp_path/'data/test.db'))
    bad=evidence_record(evidence_id='BAD')
    del bad['T10_CHANGE']
    r=c.put('/api/evidence/BAD',headers={'X-AMX-Admin':'secret'},json=bad)
    assert r.status_code==422


def test_truth_screen_without_native_t10_is_explicit_hold(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "operator-test")
    c=client(tmp_path)
    c.headers["X-AMX-Admin"]="operator-test"
    op=c.get('/api/operator/state').json()
    assert op['system_truth_t10']['T10_PASS']=='HOLD'
    assert 'without native T10' in op['system_truth_t10']['T10_ACTUAL']


def test_t10_endpoint_and_house_bootstrap(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "operator-test")
    c=client(tmp_path)
    c.headers["X-AMX-Admin"]="operator-test"
    t=c.get('/api/t10')
    assert t.status_code==200
    assert t.json()['coverage']['coverage_complete'] is True
    b=c.get('/api/house/bootstrap')
    assert b.status_code==200
    assert b.json()['controls']['no_false_live_state'] is True
    assert b.json()['controls']['t10_outcome_truth'] is True
    assert b.json()['controls']['remediation_requires_original_condition_retest'] is True
    assert b.json()['t10']['coverage']['complete_records']==1
    h=c.get('/house')
    assert h.status_code==200
    assert 'house' in h.text


def test_single_opportunity_read_cannot_bypass_t10(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "operator-test")
    c=client(tmp_path)
    c.headers["X-AMX-Admin"]="operator-test"
    r=c.get('/api/opportunities/b')
    assert r.status_code==200
    body=r.json()
    assert body['record']['state']=='QUALIFIED'
    assert body['t10']['T10_PASS']=='HOLD'
    assert 'does not yet carry native T10' in body['t10']['T10_REMAINING_GAP']
    assert 'overdrive/opportunities.json::records/b' in body['t10']['T10_EVIDENCE']


def test_public_github_state_resolves_branch_to_immutable_sha_once(tmp_path, monkeypatch):
    monkeypatch.setenv('AMX_GITHUB_REPO','amillimatrix-eng/CARBON-Creation-Hub')
    monkeypatch.setenv('AMX_GITHUB_REF','main')
    monkeypatch.delenv('AMX_GITHUB_TOKEN', raising=False)
    calls=[]
    sha='1234567890abcdef1234567890abcdef12345678'

    class FakeResponse:
        def __init__(self, payload):
            self.payload=payload
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self):
            return self.payload

    def fake_urlopen(req, timeout=10):
        headers={k.lower():v for k,v in req.header_items()}
        calls.append((req.full_url,headers))
        if 'github.com/amillimatrix-eng/CARBON-Creation-Hub/commit/main' in req.full_url:
            html=f'<meta property="og:url" content="/amillimatrix-eng/CARBON-Creation-Hub/commit/{sha}">'
            return FakeResponse(html.encode())
        return FakeResponse(b'{"schema":"AMX_MATRIX_TRUTH_SCREEN_V2"}')

    monkeypatch.setattr('backend.state.urllib.request.urlopen', fake_urlopen)
    reader=StateReader(tmp_path)
    first=reader._github_json('CONTINUITY/MATRIX_TRUTH_SCREEN.json')
    second=reader._github_json('overdrive/opportunities.json')
    assert first['schema']=='AMX_MATRIX_TRUTH_SCREEN_V2'
    assert second['schema']=='AMX_MATRIX_TRUTH_SCREEN_V2'
    resolver_calls=[x for x in calls if 'github.com/amillimatrix-eng/CARBON-Creation-Hub/commit/main' in x[0]]
    raw_calls=[x for x in calls if 'raw.githubusercontent.com' in x[0]]
    assert len(resolver_calls)==1
    assert len(raw_calls)==2
    assert all('/'+sha+'/' in url for url,_ in raw_calls)
    assert all('?amx_t=' in url for url,_ in raw_calls)
    assert all(headers['cache-control']=='no-cache' for _,headers in calls)
    assert all(headers['pragma']=='no-cache' for _,headers in calls)
    assert reader.resolved_ref==sha


def test_public_github_ref_resolution_fails_closed_without_sha(tmp_path, monkeypatch):
    monkeypatch.setenv('AMX_GITHUB_REPO','amillimatrix-eng/CARBON-Creation-Hub')
    monkeypatch.setenv('AMX_GITHUB_REF','main')
    monkeypatch.delenv('AMX_GITHUB_TOKEN', raising=False)

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self):
            return b'<html><title>no commit marker</title></html>'

    monkeypatch.setattr('backend.state.urllib.request.urlopen', lambda req, timeout=10: FakeResponse())
    reader=StateReader(tmp_path)
    try:
        reader._resolve_public_ref()
        assert False, 'expected ValueError'
    except ValueError as exc:
        assert 'did not expose' in str(exc)


def test_emailed_root_redirects_to_existing_house(tmp_path):
    c = client(tmp_path)
    entry = c.get("/", follow_redirects=False)
    assert entry.status_code == 307
    assert entry.headers["location"] == "/house"
    page = c.get("/")
    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert "house" in page.text


def test_root_reports_unavailable_house_without_false_success(tmp_path):
    c = client(tmp_path)
    (tmp_path / "house/remediation/index.html").unlink()
    entry = c.get("/", follow_redirects=False)
    assert entry.status_code == 503
    assert entry.json()["detail"] == "House interface unavailable"
