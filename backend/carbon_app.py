from pathlib import Path

from .app import app
from .marketplace import mount_marketplace

# Extend the existing provider-neutral backend. Importing this module does not
# alter backend.app:app, so legacy tests and routes retain their existing surface.
mount_marketplace(app, Path(app.state.repo_root))
