"""Eligibility gate for the existing CARBON source exchange; provider != authority."""
from __future__ import annotations
import re

LIFECYCLES = {"CURRENT_ACCEPTED_REFERENCE", "PROJECT_REFERENCE", "LEGACY_SALVAGE",
              "REJECTED_REFERENCE", "UNCLASSIFIED_REFERENCE", "PROVIDER_OUTPUT_QUARANTINE"}


def asset_eligibility(asset: dict) -> dict:
    if not asset.get("asset_id") or not asset.get("project") or asset.get("lifecycle_class") not in LIFECYCLES:
        raise ValueError("PROJECT_LIFECYCLE_CLASSIFICATION_REQUIRED")
    holds=[]
    if asset["lifecycle_class"] in {"LEGACY_SALVAGE","REJECTED_REFERENCE","UNCLASSIFIED_REFERENCE","PROVIDER_OUTPUT_QUARANTINE"}:
        holds.append("REFERENCE_QUARANTINE_NOT_CURRENT_PRODUCTION")
    if asset.get("rights_state") != "ACCEPTED" or not asset.get("rights_receipt"):
        holds.append("RIGHTS_ACCEPTANCE_REQUIRED")
    if asset.get("provider_rendered") or asset.get("watermark_or_branding"):
        holds.append("CARBON_REBUILD_FROM_GOVERNED_SOURCES_REQUIRED")
    if not asset.get("carbon_rebuild_receipt") or not asset.get("critic_receipt"):
        holds.append("REBUILD_AND_CRITIC_RECEIPTS_REQUIRED")
    return {"asset_id":asset["asset_id"],"project":asset["project"],"lifecycle_class":asset["lifecycle_class"],
            "provider_identity_role":"PROVENANCE_ONLY","automatic_canon_promotion":False,
            "notebook_eligible":asset["lifecycle_class"] in {"CURRENT_ACCEPTED_REFERENCE","PROJECT_REFERENCE"} and asset.get("rights_state")=="ACCEPTED",
            "market_master_eligible":not holds,"state":"PASS" if not holds else "HOLD",
            "unresolved_holds":holds,"attribution_must_be_preserved":True}
