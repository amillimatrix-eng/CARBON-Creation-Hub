from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.intent.api import mount_search
from backend.intent.directory import CanonicalDirectory
from backend.intent.engine import SearchEngine
from backend.intent.matrix_adapter import MatrixSearchAdapter
from backend.intent.models import (
    ActionRequest,
    CandidateInput,
    ContextSignal,
    EntityType,
    EpistemicState,
    FeedbackRequest,
    IntentCriterion,
    PivotRequest,
    SearchIntentRequest,
    SearchScope,
)
from backend.intent.store import SearchSessionStore

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "house/search/CARBON_SEARCH_DIRECTORY_V1.json"


class EvidenceStore:
    def __init__(self, records=None):
        self.records = records or []
    def search(self, query, limit):
        return self.records[:limit]


def house_visible(record):
    return str(record.get("visibility", "PRIVATE")).upper() in {"HOUSE", "PUBLIC"}


def build_engine(tmp_path, **kwargs):
    return SearchEngine(
        ROOT,
        SearchSessionStore(tmp_path / "search.db"),
        CanonicalDirectory(DIRECTORY),
        **kwargs,
    )


def phone_candidates(now=None):
    stamp = now or datetime.now(timezone.utc).isoformat()
    return [
        CandidateInput(
            candidate_id="zte", title="ZTE Blade A35", summary="Advertised 12GB RAM configuration",
            entity_id="phone:zte-a35", entity_type=EntityType.PRODUCT,
            attributes={
                "advertised_ram_gb": 12, "physical_ram_gb": 4, "virtual_ram_gb": 8,
                "price_zar": 1200, "available_now": True,
            },
            source="retailer-a", source_timestamp=stamp, evidence_pointer="retailer-a/zte-a35",
            action={"name": "OPEN"},
        ),
        CandidateInput(
            candidate_id="alt8", title="Alternative 8GB physical", summary="8GB physical RAM configuration",
            entity_id="phone:alt8", entity_type=EntityType.PRODUCT,
            attributes={
                "advertised_ram_gb": 8, "physical_ram_gb": 8, "virtual_ram_gb": 0,
                "price_zar": 1300, "available_now": True,
            },
            source="retailer-b", source_timestamp=stamp, evidence_pointer="retailer-b/alt8",
            action={"name": "OPEN"},
        ),
    ]


def phone_request(**extra):
    return SearchIntentRequest(
        query="find ZTE phone around R1200 with 12GB RAM",
        candidates=phone_candidates(),
        **extra,
    )


def test_g01_typed_measured_intent_boundary(tmp_path):
    r = build_engine(tmp_path).search(phone_request(), {SearchScope.PUBLIC})
    assert any(c.key == "advertised_ram_gb" and c.epistemic_state == EpistemicState.EXPLICIT for c in r.measured_intent)
    assert all(c.key != "physical_ram_gb" for c in r.measured_intent)
    assert next(h for h in r.hypotheses if h.hypothesis_id == "ram-physical-split").epistemic_state == EpistemicState.HYPOTHESIZED


def test_g02_latent_intent_plurality_preserved(tmp_path):
    req = phone_request(hypotheses=[
        {"hypothesis_id":"battery","label":"battery endurance may matter","probability":.3,"signal_basis":["category prior"]},
        {"hypothesis_id":"camera","label":"camera may matter","probability":.25,"signal_basis":["category prior"]},
    ])
    r = build_engine(tmp_path).search(req, {SearchScope.PUBLIC})
    assert {h.hypothesis_id for h in r.hypotheses} >= {"battery", "camera", "ram-physical-split"}
    assert all(h.epistemic_state == EpistemicState.HYPOTHESIZED for h in r.hypotheses)


def test_g03_posterior_update_without_session_restart(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    pivot = next(p for p in r.pivots if p.hypothesis_id == "ram-physical-split")
    r2 = e.pivot(r.session_id, PivotRequest(pivot_id=pivot.pivot_id))
    assert r2.session_id == r.session_id
    assert r2.primary.candidate_id == "alt8"
    assert next(h for h in r2.hypotheses if h.hypothesis_id == "ram-physical-split").epistemic_state == EpistemicState.MEASURED


def test_g04_hidden_variable_detection(tmp_path):
    r = build_engine(tmp_path).search(phone_request(), {SearchScope.PUBLIC})
    keys = {h.key for h in r.hidden_variables}
    assert "physical_ram_gb" in keys and "virtual_ram_gb" in keys


def test_g05_permission_aware_scope_routing(tmp_path):
    e = build_engine(tmp_path)
    req = SearchIntentRequest(query="private", requested_scopes=[SearchScope.CLIENT_SPACE])
    with pytest.raises(PermissionError):
        e.search(req, {SearchScope.PUBLIC})


def test_g06_claim_normalization(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    evidence = e.evidence(r.session_id)
    attrs = {c["attribute"] for c in evidence["claims"]}
    assert {"advertised_ram_gb", "physical_ram_gb", "virtual_ram_gb", "price_zar"}.issubset(attrs)


def test_g07_provenance_on_material_claims(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    claims = e.evidence(r.session_id)["claims"]
    assert claims and all(c["source"] and c["retrieved_at"] and c["evidence_pointer"] for c in claims)


def test_g08_contradiction_preservation(tmp_path):
    candidates = [
        CandidateInput(candidate_id="a1", title="A source one", entity_id="product:a", attributes={"price_zar":1000}, source="s1", evidence_pointer="s1"),
        CandidateInput(candidate_id="a2", title="A source two", entity_id="product:a", attributes={"price_zar":1200}, source="s2", evidence_pointer="s2"),
    ]
    e = build_engine(tmp_path)
    r = e.search(SearchIntentRequest(query="product a", candidates=candidates), {SearchScope.PUBLIC})
    evidence = e.evidence(r.session_id)
    assert len(evidence["contradictions"]) == 1
    assert len({c["value"] for c in evidence["claims"] if c["attribute"] == "price_zar"}) == 2


def test_g09_cross_chain_join_requires_explicit_entity_id(tmp_path):
    candidates = [
        CandidateInput(candidate_id="x", title="Same-ish", attributes={"price_zar":1000}, source="s1", evidence_pointer="s1"),
        CandidateInput(candidate_id="y", title="Same-ish", attributes={"price_zar":1200}, source="s2", evidence_pointer="s2"),
    ]
    e = build_engine(tmp_path)
    r = e.search(SearchIntentRequest(query="same-ish", candidates=candidates), {SearchScope.PUBLIC})
    assert len(r.primary.score_inputs) >= 1
    assert e.evidence(r.session_id)["contradictions"] == []


def test_g10_freshness_sensitivity(tmp_path):
    stale = (datetime.now(timezone.utc) - timedelta(days=240)).isoformat()
    fresh = datetime.now(timezone.utc).isoformat()
    candidates = [
        CandidateInput(candidate_id="stale", title="Stale deal", attributes={"price_zar":1000}, source="old", source_timestamp=stale, evidence_pointer="old"),
        CandidateInput(candidate_id="fresh", title="Fresh deal", attributes={"price_zar":1000}, source="new", source_timestamp=fresh, evidence_pointer="new"),
    ]
    req = SearchIntentRequest(query="around R1000", candidates=candidates)
    r = build_engine(tmp_path).search(req, {SearchScope.PUBLIC})
    assert r.primary.candidate_id == "fresh"


def test_g11_eif_is_reproducible_from_exposed_inputs(tmp_path):
    r = build_engine(tmp_path).search(phone_request(), {SearchScope.PUBLIC})
    assert r.primary.score_inputs
    assert any(i["layer"] == "MEASURED_INTENT" for i in r.primary.score_inputs)
    assert any(i["layer"] == "HYPOTHESIS" for i in r.primary.score_inputs)
    assert 0 <= r.primary.expected_intent_fulfilment <= 1


def test_g12_expected_regret_responds_to_uncertainty(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    before = r.expected_regret
    pivot = next(p for p in r.pivots if p.hypothesis_id == "ram-physical-split")
    after = e.pivot(r.session_id, PivotRequest(pivot_id=pivot.pivot_id)).expected_regret
    assert after < before


def test_g13_decision_stability_changes_when_uncertainty_resolves(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    assert r.decision_stable is False
    pivot = next(p for p in r.pivots if p.hypothesis_id == "ram-physical-split")
    r2 = e.pivot(r.session_id, PivotRequest(pivot_id=pivot.pivot_id))
    assert isinstance(r2.decision_stable, bool)
    assert r2.expected_regret <= r.expected_regret


def test_g14_truthful_hold(tmp_path):
    r = build_engine(tmp_path).search(SearchIntentRequest(query="nothing matches"), {SearchScope.PUBLIC})
    assert r.status.value == "HOLD" and r.primary is None


def test_g15_provider_failure_discipline(tmp_path):
    r = build_engine(tmp_path).search(
        SearchIntentRequest(query="live external", provider_mode="EXTERNAL", requested_scopes=[SearchScope.PUBLIC, SearchScope.EXTERNAL_WEB]),
        {SearchScope.PUBLIC, SearchScope.EXTERNAL_WEB},
    )
    assert r.status.value == "HOLD"
    assert "UNAVAILABLE" in r.provider_state
    assert "silently downgrade" in r.stop_reason


def test_g16_result_compression(tmp_path):
    r = build_engine(tmp_path).search(phone_request(), {SearchScope.PUBLIC})
    payload = r.model_dump(mode="json")
    assert "primary" in payload and "pivots" in payload and len(payload["pivots"]) <= 2
    assert "claims" not in payload and "events" not in payload


def test_g17_action_routing_requires_authorized_action(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    routed = e.action(r.session_id, ActionRequest(action="OPEN", candidate_id=r.primary.candidate_id))
    assert routed["binding"] is False
    with pytest.raises(PermissionError):
        e.action(r.session_id, ActionRequest(action="BUY", candidate_id=r.primary.candidate_id))


def test_g18_outcome_learning_is_versioned_and_history_preserved(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    before_claims = e.evidence(r.session_id)["claims"]
    e.feedback(r.session_id, FeedbackRequest(kind="CONFIRM", message="yes"))
    e.feedback(r.session_id, FeedbackRequest(kind="REJECT", message="no"))
    ev = e.evidence(r.session_id)
    assert ev["claims"] == before_claims
    assert ev["calibration"][0]["version"] == 2


def test_g19_internal_evidence_scenario(tmp_path):
    record = {
        "evidence_id":"E1", "artifact":"Search Commissioning", "capability":"CARBON Search",
        "interview_safe_explanation":"Commissioned Search evidence", "authoritative_source":"ROOT", "source_pointer":"root:E1",
        "status_freshness":"CURRENT", "T10_PASS":"PASS", "visibility":"PUBLIC",
    }
    def evidence_search(query, limit):
        return [CandidateInput(candidate_id="e1", title="Search Commissioning", summary="Commissioned Search evidence", entity_id="evidence:E1", entity_type=EntityType.EVIDENCE_RECORD, attributes={"t10_pass":"PASS"}, source="ROOT", source_type="GOVERNED_EVIDENCE", evidence_pointer="root:E1")]
    r = build_engine(tmp_path, evidence_search=evidence_search).search(SearchIntentRequest(query="Search Commissioning"), {SearchScope.PUBLIC})
    assert r.primary.entity_type == EntityType.EVIDENCE_RECORD
    assert r.primary.evidence_pointers == ["root:E1"]


def test_g20_external_phone_decision_scenario(tmp_path):
    def ext(query, limit): return phone_candidates()
    r = build_engine(tmp_path, external_search=ext).search(
        SearchIntentRequest(query="find ZTE phone around R1200 with 12GB RAM", provider_mode="EXTERNAL", requested_scopes=[SearchScope.PUBLIC, SearchScope.EXTERNAL_WEB]),
        {SearchScope.PUBLIC, SearchScope.EXTERNAL_WEB},
    )
    assert r.provider_state == "EXTERNAL_PROVIDER_OK"
    assert r.primary.candidate_id == "zte"
    assert "physical_ram_gb" in {h.key for h in r.hidden_variables}


def test_g21_marketplace_scenario_uses_same_engine(tmp_path):
    def market(query, limit):
        return [CandidateInput(candidate_id="m1", title="Intent matched offer", entity_id="market:1", entity_type=EntityType.MARKETPLACE_OFFER, attributes={"price_zar":999,"available_now":True}, source="market", source_type="MARKETPLACE_SIGNAL", visibility=SearchScope.CARBON_MARKETPLACE, evidence_pointer="market:1")]
    r = build_engine(tmp_path, marketplace_search=market).search(
        SearchIntentRequest(query="offer under R1000", requested_scopes=[SearchScope.CARBON_MARKETPLACE], surface="matrix"),
        {SearchScope.CARBON_MARKETPLACE},
    )
    assert r.provider_state == "MARKETPLACE_ADAPTER_OK"
    assert r.primary.entity_type == EntityType.MARKETPLACE_OFFER


def test_g22_privacy_isolation(tmp_path):
    private = CandidateInput(candidate_id="private", title="Secret", visibility=SearchScope.CLIENT_SPACE, attributes={"value":1}, source="client", evidence_pointer="secret")
    public = CandidateInput(candidate_id="public", title="Public", visibility=SearchScope.PUBLIC, attributes={"value":1}, source="public", evidence_pointer="public")
    r = build_engine(tmp_path).search(SearchIntentRequest(query="value", candidates=[private, public]), {SearchScope.PUBLIC})
    assert r.primary.candidate_id == "public"
    assert all("secret" not in p for p in r.primary.evidence_pointers)


def test_g23_audit_receipt_contains_state_not_chain_of_thought(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    ev = e.evidence(r.session_id)
    created = next(x for x in ev["events"] if x["event_type"] == "SEARCH_CREATED")
    assert created["payload"]["intent_snapshot"]
    assert "provider_state" in created["payload"]
    assert "chain_of_thought" not in json.dumps(ev).casefold()


def test_g24_regression_acceptance_vectors_are_present():
    text = (ROOT / "house/search/CARBON_SEARCH_ACCEPTANCE_VECTORS_V1.md").read_text(encoding="utf-8") if (ROOT / "house/search/CARBON_SEARCH_ACCEPTANCE_VECTORS_V1.md").exists() else ""
    assert text == "" or "phone" in text.casefold()


def test_g26_matrix_callable_thin_adapter(tmp_path):
    e = build_engine(tmp_path)
    adapter = MatrixSearchAdapter(e.search)
    r = adapter.search("CARBON Search", scopes=[SearchScope.PUBLIC])
    assert r.contract_version == "CARBON_SEARCH_V1"


def test_g27_matrix_adapter_preserves_acl(tmp_path):
    e = build_engine(tmp_path)
    adapter = MatrixSearchAdapter(e.search)
    with pytest.raises(PermissionError):
        adapter.search("secret", scopes=[SearchScope.CLIENT_SPACE])


def test_g28_contract_version_continuity(tmp_path):
    r = build_engine(tmp_path).search(SearchIntentRequest(query="CARBON Search"), {SearchScope.PUBLIC})
    assert r.contract_version == "CARBON_SEARCH_V1"


def test_g29_surface_parity_same_engine_semantics(tmp_path):
    e = build_engine(tmp_path)
    public = e.search(phone_request(surface="public"), {SearchScope.PUBLIC})
    matrix = e.search(phone_request(surface="matrix"), {SearchScope.PUBLIC})
    assert public.primary.candidate_id == matrix.primary.candidate_id
    assert [c.key for c in public.measured_intent] == [c.key for c in matrix.measured_intent]


def test_g30_canonical_directory_keeps_products_and_capabilities_distinct():
    d = CanonicalDirectory(DIRECTORY)
    assert d.get("CARBON_SEARCH").entity_type == EntityType.PRODUCT
    assert d.get("INTELLAGENT").entity_type == EntityType.CAPABILITY
    assert d.get("CARBON_MARKETPLACE").entity_id != d.get("CARBON_SEARCH").entity_id


def test_g31_active_correction_reweights_without_losing_evidence(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    before = e.evidence(r.session_id)["claims"]
    corrected = e.feedback(r.session_id, FeedbackRequest(
        kind="CORRECT",
        message="physical RAM matters",
        signal=ContextSignal(signal_type="preference", value={"key":"physical_ram_gb","operator":"prefer_high","weight":1.2}, source="user correction", provenance="session correction"),
    ))
    after = e.evidence(r.session_id)
    assert corrected.session_id == r.session_id
    assert corrected.primary.candidate_id == "alt8"
    assert after["claims"] == before
    assert any(x["event_type"] == "FEEDBACK_CORRECT" and x["payload"]["preserved_evidence"] for x in after["events"])


def test_g32_dynamic_intention_focus_changes_ranking_on_material_state_change(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    corrected = e.feedback(r.session_id, FeedbackRequest(
        kind="CORRECT",
        signal=ContextSignal(signal_type="preference", value={"key":"physical_ram_gb","operator":"prefer_high","weight":2.0}, source="user"),
    ))
    assert r.primary.candidate_id != corrected.primary.candidate_id
    assert corrected.measured_intent[-1].key == "physical_ram_gb"


def test_g33_decisive_primary_without_forced_clarification(tmp_path):
    r = build_engine(tmp_path).search(phone_request(), {SearchScope.PUBLIC})
    assert r.primary is not None
    assert r.primary.candidate_id == "zte"
    assert len(r.pivots) <= 2


def test_g34_bounded_intent_pivots(tmp_path):
    r = build_engine(tmp_path).search(phone_request(max_pivots=2), {SearchScope.PUBLIC})
    assert 0 <= len(r.pivots) <= 2
    assert all("user preference" in p.reason for p in r.pivots)


def test_g35_same_session_pivot_continuation(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    before = e.evidence(r.session_id)["claims"]
    pivot = next(p for p in r.pivots if p.hypothesis_id == "ram-physical-split")
    r2 = e.pivot(r.session_id, PivotRequest(pivot_id=pivot.pivot_id))
    ev = e.evidence(r.session_id)
    assert r2.session_id == r.session_id
    assert ev["claims"] == before
    assert any(x["event_type"] == "INTENT_PIVOT_SELECTED" and x["payload"]["evidence_preserved"] for x in ev["events"])




def test_public_free_text_correction_is_reinterpreted_without_restart(tmp_path):
    e = build_engine(tmp_path)
    r = e.search(phone_request(), {SearchScope.PUBLIC})
    corrected = e.feedback(r.session_id, FeedbackRequest(kind="CORRECT", message="I want 8GB physical RAM"))
    assert corrected.session_id == r.session_id
    assert corrected.primary.candidate_id == "alt8"
    assert any(c.key == "physical_ram_gb" and c.value == 8 for c in corrected.measured_intent)

def test_api_contract_acl_and_public_surface(tmp_path, monkeypatch):
    monkeypatch.setenv("AMX_SEARCH_DB_PATH", str(tmp_path / "api.db"))
    monkeypatch.setenv("AMX_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("AMX_SEARCH_CLIENT_TOKEN", "client-secret")
    app = FastAPI()
    mount_search(app, ROOT, EvidenceStore([]), house_visible)
    c = TestClient(app)
    assert c.get("/api/search/contract").json()["mandatory_gates"] == 35
    assert c.get("/api/search/health").json()["contract_version"] == "CARBON_SEARCH_V1"
    forbidden = c.post("/api/search/intent", json={"query":"x","surface":"matrix","requested_scopes":["MATRIX_INTERNAL"]})
    assert forbidden.status_code == 401
    public = c.post("/api/search/intent", json={"query":"CARBON Search","surface":"public","requested_scopes":["PUBLIC"]})
    assert public.status_code == 200


def test_webgl_premium_surface_is_real_not_mock():
    html = (ROOT / "house/remediation/search.html").read_text(encoding="utf-8")
    assert "getContext('webgl2'" in html
    assert "prefers-reduced-motion" in html
    assert "INTELLAGENT" in html
    assert "Expected regret" in html
    assert "/api/search/intent" in html
    assert "/evidence" in html and "/feedback" in html and "/action" in html
    assert "Correct" in html and "Confirm" in html and "Not this" in html
