from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def future():
    return (datetime.now(timezone.utc)+timedelta(minutes=90)).isoformat().replace("+00:00","Z")


def test_unknown_is_neutral_and_role_evidence_is_factual(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    seller="seller-evidence-0001"; buyer="buyer-evidence-00001"
    listing=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Tablet","price_minor":1000000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    }).json()["record"]
    assert listing["seller_evidence"]["evidence_state"]=="UNKNOWN"
    assert listing["seller_evidence"]["score"] is None

    interest=c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":50000,"at_risk_bps":3000,"proposed_start_at":future(),"proposed_duration_minutes":60,
    }).json()["record"]

    seller_view=c.get("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":seller}).json()["records"][0]
    assert seller_view["buyer_evidence"]["evidence_state"]=="UNKNOWN"
    assert seller_view["buyer_evidence"]["score"] is None

    com=c.post("/api/carbon/interests/"+interest["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30}).json()["record"]
    c.post("/api/carbon/commitments/"+com["id"]+"/confirm",headers={"X-CARBON-Actor":buyer})
    c.post("/api/carbon/commitments/"+com["id"]+"/perform",headers={"X-CARBON-Actor":buyer})
    c.post("/api/carbon/commitments/"+com["id"]+"/perform",headers={"X-CARBON-Actor":seller})

    refreshed=c.get("/api/carbon/listings/"+listing["id"]).json()
    assert refreshed["seller_evidence"]["evidence_state"]=="OBSERVED"
    assert refreshed["seller_evidence"]["honoured"]==1
    assert refreshed["seller_evidence"]["score"] is None
