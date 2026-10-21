from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def future():
    return (datetime.now(timezone.utc)+timedelta(minutes=90)).isoformat().replace("+00:00","Z")


def test_contact_is_bond_gated_and_private(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    seller="seller-message-0001"; buyer="buyer-message-00001"; stranger="stranger-message-01"
    listing=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Laptop","price_minor":1000000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    }).json()["record"]

    # No public / listing chat route exists; buyer must first create bonded interest.
    interest=c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":50000,"at_risk_bps":3000,"proposed_start_at":future(),"proposed_duration_minutes":60,
    }).json()["record"]

    sent=c.post("/api/carbon/interests/"+interest["id"]+"/messages",headers={"X-CARBON-Actor":buyer},json={"body":"Can inspect at the proposed time."})
    assert sent.status_code==200
    assert sent.json()["bond_gated"] is True
    assert sent.json()["record"]["body"]=="Can inspect at the proposed time."

    seller_view=c.get("/api/carbon/interests/"+interest["id"]+"/messages",headers={"X-CARBON-Actor":seller})
    assert seller_view.status_code==200
    assert seller_view.json()["count"]==1

    stranger_view=c.get("/api/carbon/interests/"+interest["id"]+"/messages",headers={"X-CARBON-Actor":stranger})
    assert stranger_view.status_code==403

    reply=c.post("/api/carbon/interests/"+interest["id"]+"/messages",headers={"X-CARBON-Actor":seller},json={"body":"Yes. See you then."})
    assert reply.status_code==200
    buyer_view=c.get("/api/carbon/interests/"+interest["id"]+"/messages",headers={"X-CARBON-Actor":buyer}).json()
    assert [m["body"] for m in buyer_view["records"]]==["Can inspect at the proposed time.","Yes. See you then."]
