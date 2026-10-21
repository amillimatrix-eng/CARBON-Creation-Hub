import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace
from backend.marketplace_discovery import IntentEngineDiscoveryAdapter


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_intent_adapter_posts_marketplace_candidates_and_reads_ranked_session(monkeypatch):
    calls = []
    listings = [
        {
            "id": "LISTING-1",
            "title": "Camera A",
            "description": "A mirrorless camera",
            "price_minor": 100000,
            "currency": "ZAR",
            "seller_intent": "OPEN",
            "negotiability": "NEGOTIABLE",
            "seller_ref": "private-seller-reference-must-not-be-sent",
        },
        {
            "id": "LISTING-2",
            "title": "Camera B",
            "description": "A compact camera",
            "price_minor": 90000,
            "currency": "ZAR",
            "seller_intent": "MOTIVATED",
            "negotiability": "OPEN",
            "seller_ref": "another-private-reference",
        },
    ]

    def fake_urlopen(request, timeout):
        calls.append(request)
        assert timeout == 8.0
        if request.get_method() == "POST":
            payload = json.loads(request.data.decode("utf-8"))
            assert request.full_url == "https://search.example.test/api/search/intent"
            assert any(k.lower() == "x-carbon-client" and v == "mock-client-token" for k, v in request.header_items())
            assert payload["query"] == "camera for travel"
            assert payload["surface"] == "client"
            assert payload["requested_scopes"] == ["CARBON_MARKETPLACE"]
            assert len(payload["candidates"]) == 2
            assert all(candidate["visibility"] == "CARBON_MARKETPLACE" for candidate in payload["candidates"])
            assert all(candidate["entity_type"] == "MARKETPLACE_OFFER" for candidate in payload["candidates"])
            serialized = json.dumps(payload)
            assert "private-seller-reference-must-not-be-sent" not in serialized
            assert "another-private-reference" not in serialized
            return FakeResponse({"session_id": "session-123", "status": "RESOLVED"})
        assert request.get_method() == "GET"
        assert request.full_url == "https://search.example.test/api/search/sessions/session-123"
        assert any(k.lower() == "x-carbon-client" and v == "mock-client-token" for k, v in request.header_items())
        return FakeResponse(
            {
                "session_id": "session-123",
                "status": "RESOLVED",
                "candidates": [
                    {"candidate_id": "carbon-marketplace:LISTING-2"},
                    {"candidate_id": "carbon-marketplace:LISTING-1"},
                ],
            }
        )

    monkeypatch.setattr("backend.marketplace_discovery.urllib.request.urlopen", fake_urlopen)
    adapter = IntentEngineDiscoveryAdapter("https://search.example.test/api/search/intent", "mock-client-token")

    ranked, metadata = adapter.search_with_metadata("camera for travel", listings)

    assert [record["id"] for record in ranked] == ["LISTING-2", "LISTING-1"]
    assert metadata["integration_state"] == "QUERY_VERIFIED"
    assert metadata["engine_invoked"] is True
    assert metadata["intent_session_id"] == "session-123"
    assert metadata["intent_status"] == "RESOLVED"
    assert metadata["candidate_pool_count"] == 2
    assert metadata["candidate_pool_truncated"] is False
    assert len(calls) == 2


def test_production_search_fails_closed_when_intent_endpoint_unconfigured(tmp_path, monkeypatch):
    monkeypatch.delenv("CARBON_SEARCH_INTENT_URL", raising=False)
    app = FastAPI()
    mount_marketplace(app, tmp_path, db_path=tmp_path / "market.db", demo_mode=False)
    client = TestClient(app)

    response = client.get("/api/carbon/search", params={"q": "camera"})

    assert response.status_code == 503
    assert "keyword-only fallback is disabled" in response.json()["detail"]
    assert response.json()["detail"]
