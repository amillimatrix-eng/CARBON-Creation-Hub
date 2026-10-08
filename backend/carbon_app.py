from pathlib import Path

from .app import app
from .marketplace import mount_marketplace
from .marketplace_time import sweep_marketplace_time
from .marketplace_participant import mount_participant_api

# Extend the existing provider-neutral backend instead of creating a second
# CARBON° runtime. Legacy backend.app:app remains unchanged for compatibility.
mount_marketplace(app, Path(app.state.repo_root))
mount_participant_api(app, app.state.carbon_marketplace_store)


@app.middleware("http")
async def carbon_time_boundary(request, call_next):
    if request.url.path.startswith("/api/carbon") or request.url.path.startswith("/market"):
        sweep_marketplace_time(app.state.carbon_marketplace_store)
    return await call_next(request)
