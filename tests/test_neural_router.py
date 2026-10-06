from pathlib import Path
from neural.router import exercise
def test_route_around_black(tmp_path: Path):
    r=exercise(tmp_path)
    assert r["pass"] is True
    assert r["decision"]["selected"]=="RENDER"