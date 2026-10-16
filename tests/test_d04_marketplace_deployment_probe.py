from pathlib import Path


def test_d04_marketplace_deployment_probe_contract():
    """Non-product probe: exact branch head must still expose the Marketplace mount contract."""
    carbon_app = Path("backend/carbon_app.py").read_text(encoding="utf-8")
    marketplace_index = Path("marketplace/index.html")
    assert "mount_marketplace(app" in carbon_app
    assert 'request.url.path.startswith("/market")' in carbon_app
    assert marketplace_index.is_file()
