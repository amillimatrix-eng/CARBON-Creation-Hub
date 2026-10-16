from datetime import timedelta
from pathlib import Path

from backend.marketplace import (
    CreateInterestRequest,
    CreateListingRequest,
    MarketplaceStore,
    actor_ref,
    iso,
    utcnow,
)
from backend.marketplace_time import sweep_marketplace_time


def listing_payload(ttl=15):
    return CreateListingRequest(
        title="Timed item",description="",price_minor=100000,currency="ZAR",
        seller_intent="OPEN",negotiability="OPEN",min_bond_minor=1000,
        max_considered_bond_minor=5000,min_at_risk_bps=3000,max_at_risk_bps=6000,
        commitment_ttl_minutes=ttl,
    )


def test_stale_bonded_interest_releases_without_breach(tmp_path: Path):
    store=MarketplaceStore(tmp_path/"market.db")
    seller=actor_ref("seller-time-0001")
    buyer=actor_ref("buyer-time-00001")
    listing=store.create_listing(seller,listing_payload())
    interest=store.create_interest(
        listing["id"],buyer,
        CreateInterestRequest(
            bond_minor=1000,at_risk_bps=3000,
            proposed_start_at=iso(utcnow()+timedelta(minutes=60)),
            proposed_duration_minutes=30,
        ),
        "SBX-TIME",
    )
    with store._conn() as conn:
        old=iso(utcnow()-timedelta(minutes=30))
        conn.execute("UPDATE interests SET created_at=?,updated_at=? WHERE id=?",(old,old,interest["id"]))
    changed=sweep_marketplace_time(store)
    assert changed["interest_expired"]==1
    with store._conn() as conn:
        row=conn.execute("SELECT state,provider_state FROM interests WHERE id=?",(interest["id"],)).fetchone()
    assert row["state"]=="EXPIRED_RELEASE_PENDING"
    assert row["provider_state"]=="RELEASE_PENDING_PROVIDER"


def test_expired_active_commitment_requires_review_not_auto_breach(tmp_path: Path):
    store=MarketplaceStore(tmp_path/"market.db")
    seller=actor_ref("seller-time-0001")
    buyer=actor_ref("buyer-time-00001")
    listing=store.create_listing(seller,listing_payload())
    interest=store.create_interest(
        listing["id"],buyer,
        CreateInterestRequest(
            bond_minor=1000,at_risk_bps=3000,
            proposed_start_at=iso(utcnow()+timedelta(minutes=10)),
            proposed_duration_minutes=30,
        ),
        "SBX-TIME2",
    )
    commitment=store.select_interest(interest["id"],seller,0)
    commitment=store.confirm_buyer(commitment["id"],buyer)
    with store._conn() as conn:
        past=iso(utcnow()-timedelta(minutes=1))
        conn.execute("UPDATE commitments SET end_at=? WHERE id=?",(past,commitment["id"]))
    changed=sweep_marketplace_time(store)
    assert changed["performance_review"]==1
    row=store.get_commitment(commitment["id"])
    assert row["state"]=="PERFORMANCE_REVIEW"
    assert row["resolution"]=="TIME_WINDOW_ENDED_NO_AUTOMATIC_BREACH"


def test_zero_bond_interest_expires_without_escrow_instruction(tmp_path: Path):
    store=MarketplaceStore(tmp_path/"market-zero.db")
    seller=actor_ref("seller-time-zero-01")
    buyer=actor_ref("buyer-time-zero-001")
    payload=CreateListingRequest(
        title="Open access item",description="",price_minor=100000,currency="ZAR",
        seller_intent="URGENT",negotiability="OPEN",min_bond_minor=0,
        max_considered_bond_minor=5000,min_at_risk_bps=0,max_at_risk_bps=5000,
        commitment_ttl_minutes=15,
    )
    listing=store.create_listing(seller,payload)
    interest=store.create_interest(
        listing["id"],buyer,
        CreateInterestRequest(
            bond_minor=0,at_risk_bps=0,
            proposed_start_at=iso(utcnow()+timedelta(minutes=60)),
            proposed_duration_minutes=30,
        ),
        "NO_BOND_REQUIRED","NO_BOND_REQUIRED",
    )
    with store._conn() as conn:
        old=iso(utcnow()-timedelta(minutes=30))
        conn.execute("UPDATE interests SET created_at=?,updated_at=? WHERE id=?",(old,old,interest["id"]))
    changed=sweep_marketplace_time(store)
    assert changed["interest_expired"]==1
    row=store.get_interest(interest["id"])
    assert row["state"]=="EXPIRED_RELEASE_PENDING"
    assert row["provider_state"]=="NO_BOND_REQUIRED"
