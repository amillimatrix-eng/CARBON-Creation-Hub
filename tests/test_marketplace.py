from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.marketplace import mount_marketplace


def future(minutes=60):
    return (datetime.now(timezone.utc)+timedelta(minutes=minutes)).isoformat().replace("+00:00","Z")


def client(tmp_path: Path) -> TestClient:
    app=FastAPI()
    mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=True)
    return TestClient(app)


def test_bilateral_marketplace_loop(tmp_path):
    c=client(tmp_path)
    seller="seller-secret-0001"
    buyer="buyer-secret-00001"
    r=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Laptop","description":"inspect first","price_minor":1_000_000,"currency":"ZAR",
        "seller_intent":"PATIENT","negotiability":"OPEN","min_bond_minor":50_000,
        "max_considered_bond_minor":150_000,"min_at_risk_bps":3000,"max_at_risk_bps":6000,
        "commitment_ttl_minutes":1440})
    assert r.status_code==200
    listing=r.json()["record"]; lid=listing["id"]
    assert listing["seller_ref"].startswith("C°")
    assert "seller-secret" not in str(listing)

    too_large=c.post("/api/carbon/listings/"+lid+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":500_000,"at_risk_bps":5000,"proposed_start_at":future(90),"proposed_duration_minutes":60})
    assert too_large.status_code==422
    assert "cannot buy priority" in too_large.json()["detail"]

    r=c.post("/api/carbon/listings/"+lid+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":150_000,"at_risk_bps":5000,"proposed_start_at":future(90),"proposed_duration_minutes":60})
    assert r.status_code==200
    interest=r.json()["record"]
    assert interest["considered_bond_minor"]==150_000
    assert r.json()["money_moved"] is False
    assert interest["state"]=="BONDED_INTEREST"

    r=c.post("/api/carbon/interests/"+interest["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30})
    assert r.status_code==200
    commitment=r.json()["record"]
    assert commitment["state"]=="SELECTED"
    assert r.json()["at_risk_active"] is False

    r=c.post("/api/carbon/commitments/"+commitment["id"]+"/confirm",headers={"X-CARBON-Actor":buyer})
    assert r.status_code==200
    commitment=r.json()["record"]
    assert commitment["state"]=="ACTIVE_COMMITMENT"
    assert r.json()["at_risk_active"] is True

    assert c.post("/api/carbon/commitments/"+commitment["id"]+"/perform",headers={"X-CARBON-Actor":buyer}).status_code==200
    r=c.post("/api/carbon/commitments/"+commitment["id"]+"/perform",headers={"X-CARBON-Actor":seller})
    assert r.status_code==200
    assert r.json()["record"]["state"]=="HONOURED"

    r=c.post("/api/carbon/commitments/"+commitment["id"]+"/deal",headers={"X-CARBON-Actor":buyer})
    deal=r.json()["record"]
    assert deal["state"]=="FUNDING_REQUIRED"
    funded=c.post("/api/carbon/deals/"+deal["id"]+"/fund",headers={"X-CARBON-Actor":buyer})
    assert funded.status_code==200
    deal=funded.json()["record"]
    assert deal["state"]=="INSPECTION"
    assert deal["funding_state"]=="SANDBOX_PURCHASE_FUNDS_SECURED"
    assert funded.json()["bond_and_purchase_funds_are_separate"] is True
    r=c.post("/api/carbon/deals/"+deal["id"]+"/accept",headers={"X-CARBON-Actor":buyer})
    assert r.json()["record"]["state"]=="INSPECTION"
    r=c.post("/api/carbon/deals/"+deal["id"]+"/accept",headers={"X-CARBON-Actor":seller})
    assert r.status_code==200
    assert r.json()["record"]["state"]=="BONDED_DEAL"
    assert r.json()["record"]["settlement_state"]=="SANDBOX_READY_FOR_PROVIDER"
    assert r.json()["money_moved"] is False

    events=c.get("/api/carbon/events/commitment/"+commitment["id"]).json()["records"]
    types=[e["event_type"] for e in events]
    assert "BILATERAL_COMMITMENT_ACTIVATED" in types
    assert types.count("PERFORMANCE_CONFIRMED")==2


def test_writes_fail_closed_without_demo_mode(tmp_path):
    app=FastAPI()
    mount_marketplace(app,tmp_path,db_path=tmp_path/"market.db",demo_mode=False)
    c=TestClient(app)
    r=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":"seller-secret-0001"},json={
        "title":"Laptop","price_minor":1000000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,"min_at_risk_bps":3000,"max_at_risk_bps":6000,
        "commitment_ttl_minutes":1440})
    assert r.status_code==503
    assert c.get("/api/carbon/bootstrap").json()["money_moved"] is False


def test_pre_activation_cancel_is_full_release(tmp_path):
    c=client(tmp_path)
    seller="seller-secret-0001"; buyer="buyer-secret-00001"
    listing=c.post("/api/carbon/listings",headers={"X-CARBON-Actor":seller},json={
        "title":"Camera","price_minor":2000000,"currency":"ZAR","seller_intent":"OPEN","negotiability":"OPEN",
        "min_bond_minor":50000,"max_considered_bond_minor":150000,"min_at_risk_bps":3000,"max_at_risk_bps":6000,
        "commitment_ttl_minutes":1440}).json()["record"]
    interest=c.post("/api/carbon/listings/"+listing["id"]+"/interests",headers={"X-CARBON-Actor":buyer},json={
        "bond_minor":50000,"at_risk_bps":3000,"proposed_start_at":future(120),"proposed_duration_minutes":60}).json()["record"]
    commitment=c.post("/api/carbon/interests/"+interest["id"]+"/select",headers={"X-CARBON-Actor":seller},json={"cancellation_buffer_minutes":30}).json()["record"]
    r=c.post("/api/carbon/commitments/"+commitment["id"]+"/cancel",headers={"X-CARBON-Actor":buyer},json={"reason":"changed mind before activation"})
    assert r.status_code==200
    assert r.json()["record"]["state"]=="MUTUAL_RELEASE"
    assert r.json()["record"]["resolution"]=="FULL_RELEASE_PRE_ACTIVATION"
