from pathlib import Path


def test_house_has_no_hardcoded_executing_claims():
    html=Path('house/remediation/index.html').read_text()
    assert 'iSCOPE</b><p>EXECUTING' not in html
    assert 'PRI</b><p>EXECUTING' not in html
    assert 'Evidence Terminal' in html


def test_frontend_uses_control_backend():
    js=Path('house/remediation/house.js').read_text()
    assert '/api/house/bootstrap' in js
    assert '/api/evidence/search' in js
    assert 'No cached operational claims are being presented as live.' in js
