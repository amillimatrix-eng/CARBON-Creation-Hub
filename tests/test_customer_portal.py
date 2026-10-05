import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import create_app


def portal_client(tmp_path: Path, monkeypatch) -> TestClient:
    (tmp_path / "evidence").mkdir(parents=True)
    (tmp_path / "house/remediation").mkdir(parents=True)
    (tmp_path / "evidence/index.json").write_text(json.dumps({"records": []}), encoding="utf-8")
    (tmp_path / "house/remediation/proposal.html").write_text("<html>proposal</html>", encoding="utf-8")
    private_registry = tmp_path.parent / (tmp_path.name + "-private-proposals.json")
    monkeypatch.setenv("AMX_PROPOSAL_REGISTRY_PATH", str(private_registry))
    private_registry.write_text(json.dumps({
        "schema": "AMX_CARBON_CUSTOMER_PORTAL_V1",
        "proposals": {
            "test-token": {
                "proposal_ref": "TEST-001",
                "opportunity_key": "test-opportunity",
                "thread_id": "original-thread",
                "customer_id": "verified-customer",
                "business_name": "Test Business",
                "status": "DRAFT",
                "issued_at": None,
                "validity_hours": 24,
                "modules": [
                    {"id": "SOCIAL", "name": "SOCIAL°", "selected": True},
                    {"id": "PLACE", "name": "PLACE°", "selected": False},
                ],
            }
        },
    }), encoding="utf-8")
    (tmp_path / "overdrive").mkdir()
    (tmp_path / "overdrive/opportunities.json").write_text(json.dumps({"records": {"test-opportunity": {"execution_owner": "PRI", "state": "SUBMITTED", "thread_id": "original-thread"}}}))
    return TestClient(create_app(tmp_path, tmp_path / "data/test.db"))


def test_draft_quote_does_not_start_validity_clock(tmp_path, monkeypatch):
    c = portal_client(tmp_path, monkeypatch)
    r = c.get("/api/proposals/test-token")
    assert r.status_code == 200
    body = r.json()
    assert body["quote_status"] == "DRAFT_NOT_ISSUED"
    assert body["valid_until"] is None
    assert body["validity_hours"] == 24


def test_customer_portal_route_and_unknown_token(tmp_path, monkeypatch):
    c = portal_client(tmp_path, monkeypatch)
    r = c.get("/proposal/test-token")
    assert r.status_code == 200
    assert "proposal" in r.text
    assert c.get("/proposal/nope").status_code == 404


def test_change_request_is_non_binding_and_filters_unknown_modules(tmp_path, monkeypatch):
    c = portal_client(tmp_path, monkeypatch)
    r = c.post("/api/proposals/test-token/request-change", json={
        "selected_modules": ["SOCIAL", "UNKNOWN"],
        "message": "Add PLACE later.",
        "contact": "customer@example.com",
        "action": "REQUEST_CHANGE",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["received"] is True
    assert body["binding"] is False
    receipt_path = tmp_path / "data/proposal_requests.jsonl"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8").splitlines()[-1])
    assert receipt["selected_modules"] == ["SOCIAL"]
    assert receipt["binding"] is False
    assert "does not automatically" in receipt["note"]
