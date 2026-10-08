from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def iso_future(minutes):
    return (datetime.now(timezone.utc)+timedelta(minutes=minutes)).isoformat().replace("+00:00","Z")


def active_commitment(c,seller,buyer):
    l=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Timed laptop","price_minor":1000000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    }).json()["record"]
    i=c.post("/api/carbon/listings/"+l["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":50000,"at_risk_bps":3000,"proposed_start_at":iso_future(90),"proposed_duration_minutes":60,
    }).json()["record"]
    com=c.post("/api/carbon/interests/"+i["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30}).json()["record"]
    return c.post("/api/carbon/commitments/"+com["id"]+"/confirm",headers={"X-CARBON-Actor":buyer}).json()["record"]


def test_extension_requires_counterparty_acceptance(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    seller="seller-extend-0001"; buyer="buyer-extend-00001"
    com=active_commitment(c,seller,buyer)
    old_start=com["start_at"]

    req=c.post("/api/carbon/commitments/"+com["id"]+"/extensions",headers={"X-CARBON-Actor":buyer},json={
        "proposed_start_at":iso_future(180),"proposed_duration_minutes":90,"reason":"traffic delay"
    })
    assert req.status_code==200
    ext=req.json()["record"]
    assert ext["status"]=="PENDING"

    unchanged=c.get("/api/carbon/commitments/"+com["id"]).json()
    assert unchanged["start_at"]==old_start

    self_approve=c.post("/api/carbon/extensions/"+ext["id"]+"/respond",headers={"X-CARBON-Actor":buyer},json={"action":"ACCEPT"})
    assert self_approve.status_code==403

    accepted=c.post("/api/carbon/extensions/"+ext["id"]+"/respond",headers={"X-CARBON-Actor":seller},json={"action":"ACCEPT"})
    assert accepted.status_code==200
    assert accepted.json()["record"]["status"]=="ACCEPTED"
    updated=c.get("/api/carbon/commitments/"+com["id"]).json()
    assert updated["start_at"]==ext["proposed_start_at"]
    assert updated["end_at"]==ext["proposed_end_at"]
