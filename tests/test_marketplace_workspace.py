from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace
from backend.marketplace_workspace import mount_workspace_api


ACTOR_SECRET = "workspace-owner-secret-01"


def make_client(tmp_path: Path, *, demo_mode: bool) -> TestClient:
    root = tmp_path / ("demo" if demo_mode else "production")
    root.mkdir(parents=True, exist_ok=True)
    app = FastAPI()
    mount_marketplace(
        app,
        root,
        db_path=root / "market.db",
        demo_mode=demo_mode,
    )
    mount_workspace_api(app, app.state.carbon_marketplace_store)
    return TestClient(app)


def test_projects_and_media_reads_work_in_explicit_demo_mode(tmp_path):
    client = make_client(tmp_path, demo_mode=True)
    headers = {"X-CARBON-Actor": ACTOR_SECRET}

    projects = client.get("/api/carbon/projects", headers=headers)
    media = client.get("/api/carbon/media", headers=headers)

    assert projects.status_code == 200, projects.text
    assert projects.json()["count"] == 0
    assert projects.json()["records"] == []
    assert media.status_code == 200, media.text
    assert media.json()["count"] == 0
    assert media.json()["records"] == []


def test_projects_and_media_require_actor_even_in_demo_mode(tmp_path):
    client = make_client(tmp_path, demo_mode=True)

    assert client.get("/api/carbon/projects").status_code == 401
    assert client.get("/api/carbon/media").status_code == 401


def test_projects_and_media_remain_fail_closed_outside_demo_mode(tmp_path):
    client = make_client(tmp_path, demo_mode=False)
    headers = {"X-CARBON-Actor": ACTOR_SECRET}

    assert client.get("/api/carbon/projects", headers=headers).status_code == 503
    assert client.get("/api/carbon/media", headers=headers).status_code == 503
