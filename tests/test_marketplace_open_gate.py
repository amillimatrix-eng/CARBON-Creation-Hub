from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def future():
    return (datetime.now(timezone.utc)+timedelta(minutes=90)).isoformat().replace("+00:00","Z")


def test_seller_can_choose_zero_money_access_gate(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    seller="seller-open-gate-0001"; buyer="buyer-open-gate-00001"
    listing=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Quick sale","price_minor":250000,"currency":"ZAR","seller_intent":"URGENT","negotiability":"NEGOTIABLE",
        "min_bond_minor":0,"max_considered_bond_minor":50000,
        "min_at_risk_bps":0,"max_at_risk_bps":5000,"commitment_ttl_minutes":240,
    }).json()["record"]
    response=c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":0,"at_risk_bps":0,"proposed_start_at":future(),"proposed_duration_minutes":30,
    })
    assert response.status_code==200
    assert response.json()["money_instruction"] is None
    interest=response.json()["record"]
    assert interest["state"]=="QUALIFIED_INTEREST"
    assert interest["provider_state"]=="NO_BOND_REQUIRED"

    message=c.post("/api/carbon/interests/"+interest["id"]+"/messages",headers={"X-CARBON-Actor":buyer},json={"body":"Can collect at the proposed time."})
    assert message.status_code==200

    selected=c.post("/api/carbon/interests/"+interest["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30})
    assert selected.status_code==200
    assert selected.json()["record"]["at_risk_minor"]==0
