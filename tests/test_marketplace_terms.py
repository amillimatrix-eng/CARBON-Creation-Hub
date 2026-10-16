import hashlib
import json
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def future():
    return (datetime.now(timezone.utc)+timedelta(minutes=90)).isoformat().replace("+00:00","Z")


def test_bilateral_terms_are_snapshotted_and_hashed(tmp_path):
    app=FastAPI(); mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True); c=TestClient(app)
    seller="seller-terms-0001"; buyer="buyer-terms-00001"
    listing=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Specific laptop","description":"16GB RAM, charger included",
        "price_minor":1200000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,
        "min_at_risk_bps":3000,"max_at_risk_bps":6000,"commitment_ttl_minutes":1440,
    }).json()["record"]
    interest=c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":75000,"at_risk_bps":4000,"proposed_start_at":future(),"proposed_duration_minutes":60,
    }).json()["record"]
    commitment=c.post("/api/carbon/interests/"+interest["id"]+"/select",headers={"X-CARBON-Actor":seller},json={
        "cancellation_buffer_minutes":30,
    }).json()["record"]
    terms=json.loads(commitment["terms_json"])
    assert terms["seller"]["reserves_opportunity_for_active_window"] is True
    assert terms["seller"]["must_present_item_materially_as_listed"] is True
    assert terms["buyer"]["at_risk_bps"]==4000
    assert terms["item"]["price_minor"]==1200000
    canonical=json.dumps(terms,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    assert commitment["terms_hash"]==hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    activated=c.post("/api/carbon/commitments/"+commitment["id"]+"/confirm",headers={"X-CARBON-Actor":buyer}).json()["record"]
    events=c.get("/api/carbon/events/commitment/"+commitment["id"]).json()["records"]
    activated_event=[e for e in events if e["event_type"]=="BILATERAL_COMMITMENT_ACTIVATED"][0]
    assert activated_event["payload"]["terms_hash"]==activated["terms_hash"]
