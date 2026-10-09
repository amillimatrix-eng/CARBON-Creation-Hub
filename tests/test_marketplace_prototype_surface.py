from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace
from backend.marketplace_participant import mount_participant_api


def client(tmp_path: Path) -> TestClient:
    app = FastAPI()
    mount_marketplace(app, tmp_path, db_path=tmp_path / "market.db", demo_mode=True)
    mount_participant_api(app, app.state.carbon_marketplace_store)
    return TestClient(app)


def test_demo_market_is_image_bearing_and_searchable(tmp_path):
    c = client(tmp_path)
    seeded = c.post("/api/carbon/demo/seed")
    assert seeded.status_code == 200
    listings = seeded.json()["listings"]
    assert len(listings) >= 3
    assert all(record["image_urls"] for record in listings)

    found = c.get("/api/carbon/search", params={"q": "Sony"})
    assert found.status_code == 200
    payload = found.json()
    assert payload["count"] == 1
    assert payload["records"][0]["title"] == "Sony A7 IV body"
    assert payload["discovery"]["result_contract"] == "CARBON_LISTING_V1"
    assert payload["discovery"]["external_search_connected"] is False


def test_media_upload_uses_provider_seam(tmp_path):
    c = client(tmp_path)
    response = c.post(
        "/api/carbon/media",
        headers={"X-CARBON-Actor": "seller-secret-0001"},
        files={"files": ("item.png", b"not-a-real-png-but-provider-boundary-test", "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["urls"][0].startswith("/market/media/")
    assert payload["storage"]["name"] == "LOCAL_MEDIA"
    assert payload["storage"]["durable"] is False
    assert "production_seam" in payload


def test_profile_thumbnail_and_behavior_projection(tmp_path):
    c = client(tmp_path)
    actor = "buyer-secret-00001"
    initial = c.get("/api/carbon/me", headers={"X-CARBON-Actor": actor})
    assert initial.status_code == 200
    assert initial.json()["profile"]["display_name"] == ""
    assert initial.json()["role_evidence"]["buyer"]["evidence_state"] == "UNKNOWN"

    updated = c.post(
        "/api/carbon/me/profile",
        headers={"X-CARBON-Actor": actor},
        json={"display_name": "Mi Buyer", "avatar_url": "/market/media/demo-avatar.webp"},
    )
    assert updated.status_code == 200
    profile = updated.json()["profile"]
    assert profile["display_name"] == "Mi Buyer"
    assert profile["avatar_url"] == "/market/media/demo-avatar.webp"
    assert updated.json()["summary"]["recorded_actions"] == 0
