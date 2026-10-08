from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, Header, HTTPException

from .marketplace import MarketplaceStore, actor_ref


def participant_projection(store: MarketplaceStore, participant_ref: str) -> dict[str, Any]:
    with store._conn() as conn:
        listings=[dict(r) for r in conn.execute(
            "SELECT * FROM listings WHERE seller_ref=? ORDER BY updated_at DESC",
            (participant_ref,),
        ).fetchall()]
        interests=[dict(r) for r in conn.execute(
            "SELECT * FROM interests WHERE buyer_ref=? ORDER BY updated_at DESC",
            (participant_ref,),
        ).fetchall()]
        commitments=[dict(r) for r in conn.execute(
            """SELECT * FROM commitments
               WHERE buyer_ref=? OR seller_ref=?
               ORDER BY updated_at DESC""",
            (participant_ref,participant_ref),
        ).fetchall()]
        deals=[dict(r) for r in conn.execute(
            """SELECT * FROM deals
               WHERE buyer_ref=? OR seller_ref=?
               ORDER BY updated_at DESC""",
            (participant_ref,participant_ref),
        ).fetchall()]
        extensions=[dict(r) for r in conn.execute(
            """SELECT e.* FROM extension_requests e
               JOIN commitments c ON c.id=e.commitment_id
               WHERE c.buyer_ref=? OR c.seller_ref=?
               ORDER BY e.updated_at DESC""",
            (participant_ref,participant_ref),
        ).fetchall()]

        event_count=conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE actor_ref=?",
            (participant_ref,),
        ).fetchone()["n"]

    honoured=sum(1 for c in commitments if c["state"]=="HONOURED")
    active=sum(1 for c in commitments if c["state"]=="ACTIVE_COMMITMENT")
    valid_exits=sum(1 for c in commitments if c["state"] in {"VALID_EXIT","MUTUAL_RELEASE"})
    reviews=sum(1 for c in commitments if c["state"] in {"BUYER_BREACH_REVIEW","SELLER_BREACH_REVIEW","PERFORMANCE_REVIEW","DISPUTED"})
    bonded_deals=sum(1 for d in deals if d["state"]=="BONDED_DEAL")

    return {
        "actor_ref":participant_ref,
        "roles":{
            "seller":bool(listings),
            "buyer":bool(interests),
        },
        "summary":{
            "listings":len(listings),
            "interests":len(interests),
            "active_commitments":active,
            "honoured_commitments":honoured,
            "valid_exits":valid_exits,
            "review_states":reviews,
            "bonded_deals":bonded_deals,
            "recorded_actions":int(event_count or 0),
        },
        "listings":listings,
        "interests":interests,
        "commitments":commitments,
        "deals":deals,
        "extensions":extensions,
        "note":"This is transaction evidence, not a universal reputation score.",
    }


def mount_participant_api(app: FastAPI, store: MarketplaceStore) -> None:
    router=APIRouter()

    def current_actor(x_carbon_actor: str | None = Header(default=None)) -> str:
        if not x_carbon_actor:
            raise HTTPException(status_code=401,detail="X-CARBON-Actor is required")
        try:
            return actor_ref(x_carbon_actor)
        except ValueError as exc:
            raise HTTPException(status_code=401,detail=str(exc)) from exc

    @router.get("/api/carbon/me")
    def me(x_carbon_actor: str | None = Header(default=None)) -> dict[str, Any]:
        return participant_projection(store,current_actor(x_carbon_actor))

    app.include_router(router)
