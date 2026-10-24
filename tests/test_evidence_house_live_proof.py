from pathlib import Path
import re

PAGE = Path("customer-directory/work/evidence-house.html").read_text(encoding="utf-8")


def test_evidence_house_stays_noindex_and_uses_exact_public_allowlist():
    assert re.search(r'<meta\s+name="robots"\s+content="noindex,nofollow"', PAGE, re.IGNORECASE)
    match = re.search(r"var\s+allowed\s*=\s*\{(.*?)\n\s*\};", PAGE, re.DOTALL)
    assert match, "The public-safe allowlist must remain explicit and auditable."
    evidence_ids = re.findall(r'"(EVID-[A-Z0-9-]+)"\s*:', match.group(1))
    assert len(evidence_ids) == 3
    assert set(evidence_ids) == {
        "EVID-COMMERCIAL-001",
        "EVID-BUILD-DELIVERY-001",
        "EVID-OVERDRIVE-001",
    }


def test_public_index_fetch_fails_closed_and_filters_before_rendering():
    assert 'fetch("https://raw.githubusercontent.com/amillimatrix-eng/CARBON-Creation-Hub/main/evidence/index.json"' in PAGE
    assert 'credentials:"omit"' in PAGE
    assert 'mode:"cors"' in PAGE
    assert 'cache:"no-store"' in PAGE
    assert "data.records.filter(function(r){return Object.prototype.hasOwnProperty.call(allowed,r.evidence_id);});" in PAGE
    assert "Public-safe evidence unavailable" in PAGE
    assert "No result is inferred." in PAGE


def test_untrusted_record_values_use_text_nodes_not_html_injection():
    assert "n.textContent=String(txt)" in PAGE
    assert "results.replaceChildren()" in PAGE
    assert "innerHTML" not in PAGE.lower()
    assert 'a.rel="noopener noreferrer"' in PAGE
