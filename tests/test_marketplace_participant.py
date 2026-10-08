from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace
from backend.marketplace_participant import mount_participant_api


def future():
    return (datetime.now(timezone.utc)+timedelta(minutes=60)).isoformat().replace("+00:00","Z")


def test_participant_projection_is_private_to_actor(tmp_path):
    app=FastAPI()
    mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True)
    mount_participant_api(app,app.state.carbon_marketplace_store)
    c=TestClient(app)
    seller="seller-private-0001"
    buyer="buyer-private-00001"

    listing=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Phone","price_minor":1000000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    }).json()["record"]

    c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":50000,"at_risk_bps":3000,"proposed_start_at":future(),"proposed_duration_minutes":60,
    })

    buyer_me=c.get("/api/carbon/me",headers={"X-CARBON-Actor":buyer})
    assert buyer_me.status_code==200
    assert buyer_me.json()["summary"]["interests"]==1
    assert buyer_me.json()["summary"]["listings"]==0
    assert "buyer-private" not in str(buyer_me.json())

    seller_me=c.get("/api/carbon/me",headers={"X-CARBON-Actor":seller})
    assert seller_me.status_code==200
    assert seller_me.json()["summary"]["listings"]==1
    assert seller_me.json()["summary"]["interests"]==0
    assert seller_me.json()["note"].endswith("not a universal reputation score.")
