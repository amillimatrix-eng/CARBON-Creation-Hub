from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def future(minutes=90):
    return (datetime.now(timezone.utc)+timedelta(minutes=minutes)).isoformat().replace("+00:00","Z")


def listing(c,seller):
    return c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Single camera","price_minor":1500000,"currency":"ZAR",
        "seller_intent":"MOTIVATED","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    }).json()["record"]


def interest(c,lid,buyer,amount=50000):
    return c.post("/api/carbon/listings/"+lid+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":amount,"at_risk_bps":3000,"proposed_start_at":future(),"proposed_duration_minutes":60,
    }).json()["record"]


def test_one_active_buyer_and_clean_no_deal_handoff(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    seller="seller-queue-0001"; b1="buyer-queue-00001"; b2="buyer-queue-00002"
    l=listing(c,seller); i1=interest(c,l["id"],b1); i2=interest(c,l["id"],b2,100000)

    com1=c.post("/api/carbon/interests/"+i1["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30}).json()["record"]
    blocked=c.post("/api/carbon/interests/"+i2["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30})
    assert blocked.status_code==422
    assert "remain queued" in blocked.json()["detail"]

    c.post("/api/carbon/commitments/"+com1["id"]+"/confirm",headers={"X-CARBON-Actor":b1})
    c.post("/api/carbon/commitments/"+com1["id"]+"/perform",headers={"X-CARBON-Actor":b1})
    c.post("/api/carbon/commitments/"+com1["id"]+"/perform",headers={"X-CARBON-Actor":seller})
    deal=c.post("/api/carbon/commitments/"+com1["id"]+"/deal",headers={"X-CARBON-Actor":b1}).json()["record"]
    no_deal=c.post("/api/carbon/deals/"+deal["id"]+"/decline",headers={"X-CARBON-Actor":b1},json={"reason":"item not right for me"})
    assert no_deal.status_code==200
    assert no_deal.json()["record"]["state"]=="NO_DEAL"

    next_pick=c.post("/api/carbon/interests/"+i2["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30})
    assert next_pick.status_code==200
    assert next_pick.json()["record"]["state"]=="SELECTED"
