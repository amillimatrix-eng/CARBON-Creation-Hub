from __future__ import annotations

from datetime import timedelta

from .marketplace import MarketplaceStore, iso, parse_time, utcnow


def sweep_marketplace_time(store: MarketplaceStore) -> dict[str, int]:
    """Resolve expired time-bound states without inventing fault.

    - Unselected bonded interest expires to release-pending.
    - Seller-selected interest that never becomes bilateral before start releases.
    - Active commitments past their end become PERFORMANCE_REVIEW, never an
      automatic buyer/seller breach.
    """
    now=utcnow()
    changed={"interest_expired":0,"selection_expired":0,"performance_review":0}
    with store._conn() as conn:
        pending=conn.execute(
            """SELECT i.*, l.commitment_ttl_minutes
               FROM interests i JOIN listings l ON l.id=i.listing_id
               WHERE i.state='BONDED_INTEREST'"""
        ).fetchall()
        for row in pending:
            created=parse_time(row["created_at"])
            expiry=min(
                created+timedelta(minutes=int(row["commitment_ttl_minutes"])),
                parse_time(row["proposed_start_at"]),
            )
            if now < expiry:
                continue
            stamp=iso(now)
            conn.execute(
                "UPDATE interests SET state='EXPIRED_RELEASE_PENDING',provider_state='SANDBOX_RELEASE_PENDING',updated_at=? WHERE id=?",
                (stamp,row["id"]),
            )
            store._event(conn,"interest",row["id"],"SYSTEM","BONDED_INTEREST_EXPIRED",{
                "resolution":"FULL_RELEASE_PENDING",
                "money_moved":False,
                "expired_at":stamp,
            })
            changed["interest_expired"]+=1

        selected=conn.execute("SELECT * FROM commitments WHERE state='SELECTED'").fetchall()
        for row in selected:
            if now < parse_time(row["start_at"]):
                continue
            stamp=iso(now)
            conn.execute(
                "UPDATE commitments SET state='MUTUAL_RELEASE',resolution='FULL_RELEASE_SELECTION_EXPIRED',updated_at=? WHERE id=?",
                (stamp,row["id"]),
            )
            conn.execute(
                "UPDATE interests SET state='RELEASE_PENDING',provider_state='SANDBOX_RELEASE_PENDING',updated_at=? WHERE id=?",
                (stamp,row["interest_id"]),
            )
            store._event(conn,"commitment",row["id"],"SYSTEM","SELECTION_EXPIRED",{
                "buyer_consequence_activated":False,
                "resolution":"FULL_RELEASE_SELECTION_EXPIRED",
            })
            changed["selection_expired"]+=1

        active=conn.execute("SELECT * FROM commitments WHERE state='ACTIVE_COMMITMENT'").fetchall()
        for row in active:
            if now < parse_time(row["end_at"]):
                continue
            stamp=iso(now)
            conn.execute(
                "UPDATE commitments SET state='PERFORMANCE_REVIEW',resolution='TIME_WINDOW_ENDED_NO_AUTOMATIC_BREACH',updated_at=? WHERE id=?",
                (stamp,row["id"]),
            )
            conn.execute(
                "UPDATE interests SET state='REVIEW_PENDING',provider_state='SANDBOX_HOLD',updated_at=? WHERE id=?",
                (stamp,row["interest_id"]),
            )
            store._event(conn,"commitment",row["id"],"SYSTEM","PERFORMANCE_WINDOW_ENDED",{
                "resolution":"REVIEW_REQUIRED",
                "automatic_breach":False,
            })
            changed["performance_review"]+=1
    return changed
