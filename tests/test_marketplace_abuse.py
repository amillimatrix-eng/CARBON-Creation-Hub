from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def future():
    return (datetime.now(timezone.utc)+timedelta(minutes=90)).isoformat().replace("+00:00","Z")


def test_listing_bond_cannot_exceed_sale_value(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    bad=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":"seller-abuse-0001"},json={
        "title":"R100 item","price_minor":10000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":5000,"max_considered_bond_minor":20000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    })
    assert bad.status_code==422


def test_buyer_cannot_spam_parallel_bonds_on_same_listing(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    seller="seller-abuse-0001"; buyer="buyer-abuse-00001"
    listing=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Console","price_minor":1000000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    }).json()["record"]
    payload={"bond_minor":50000,"at_risk_bps":3000,"proposed_start_at":future(),"proposed_duration_minutes":60}
    first=c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json=payload)
    assert first.status_code==200
    second=c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json=payload)
    assert second.status_code==422
    assert "unresolved interest" in second.json()["detail"]
