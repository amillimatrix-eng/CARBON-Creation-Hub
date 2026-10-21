from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MANDATE_ID = "AMX-MANDATE-MATRIX-CRITIC-V1"


def extract_critic_mandate_sha(blue_state: str) -> str:
    headings = list(re.finditer(r"(?m)^## .+$", blue_state))
    for index, heading in enumerate(headings):
        if heading.group(0).strip() == "## MATRIX CRITIC":
            end = headings[index + 1].start() if index + 1 < len(headings) else len(blue_state)
            section = blue_state[heading.end():end]
            match = re.search(r"\*\*SHA-256:\*\*\s*`([0-9a-f]{64})`", section)
            if match:
                return match.group(1)
            raise ValueError("MATRIX CRITIC section exists but does not declare a mandate SHA-256")
    raise ValueError("MATRIX CRITIC section not found in current Blue State")


def _single_marker(body: str, marker: str) -> str | None:
    values = re.findall(rf"(?m)^{re.escape(marker)}:\s*(.*?)\s*$", body or "")
    if len(values) != 1:
        return None
    return values[0].strip()


def evaluate_critic_reviews(
    reviews: list[dict[str, Any]],
    *,
    critic_login: str,
    pr_author: str,
    head_sha: str,
    mandate_sha: str,
) -> tuple[bool, str]:
    if not critic_login.strip():
        return False, "Repository variable MATRIX_CRITIC_REVIEWER is not configured; fail closed."
    if critic_login.casefold() == pr_author.casefold():
        return False, "Configured critic identity is the PR author; independent self-approval is not allowed."

    matches = [
        review for review in reviews
        if str((review.get("user") or {}).get("login", "")).casefold() == critic_login.casefold()
    ]
    if not matches:
        return False, f"No review from configured Matrix Critic reviewer {critic_login!r}."

    # The newest review by the configured critic controls. An older approval cannot
    # survive a later HOLD / REQUEST_CHANGES / COMMENT or an update to the PR head.
    latest = max(matches, key=lambda item: (item.get("submitted_at") or "", int(item.get("id") or 0)))
    if str(latest.get("state", "")).upper() != "APPROVED":
        return False, f"Latest Matrix Critic review is {latest.get('state')!r}, not APPROVED."
    if latest.get("commit_id") != head_sha:
        return False, "Matrix Critic approval is not bound to the exact current PR head SHA."

    body = str(latest.get("body") or "")
    expected = {
        "MATRIX-CRITIC-RESULT": "APPROVE",
        "MATRIX-CRITIC-MANDATE": MANDATE_ID,
        "MATRIX-CRITIC-MANDATE-SHA256": mandate_sha,
        "MATRIX-CRITIC-REVIEWED-HEAD": head_sha,
    }
    for marker, value in expected.items():
        actual = _single_marker(body, marker)
        if actual != value:
            return False, f"Matrix Critic review missing or mismatches {marker} for the current head/mandate."

    receipt = _single_marker(body, "MATRIX-CRITIC-RECEIPT")
    if not receipt or receipt.casefold() in {"none", "unknown", "tbd", "pending", "n/a"}:
        return False, "Matrix Critic approval has no durable evidence/receipt pointer."
    if not (receipt.startswith("https://") or receipt.startswith("AMX/ROOT/") or receipt.startswith("governance/")):
        return False, "Matrix Critic receipt pointer must be an HTTPS URL or a governed repository path."
    return True, f"Independent Matrix Critic approval verified for {head_sha} with receipt {receipt}."


def _fetch_reviews(repo: str, pr_number: int, token: str, api_url: str) -> list[dict[str, Any]]:
    all_reviews: list[dict[str, Any]] = []
    page = 1
    while True:
        url = f"{api_url.rstrip('/')}/repos/{repo}/pulls/{pr_number}/reviews?per_page=100&page={page}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "AMX-Matrix-Critic-Release-Gate",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                batch = json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"Could not retrieve PR reviews from GitHub API: {exc}") from exc
        if not isinstance(batch, list):
            raise RuntimeError("GitHub reviews API did not return a JSON list")
        all_reviews.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return all_reviews


def main() -> int:
    env = os.environ
    required = ["GITHUB_REPOSITORY", "GITHUB_TOKEN", "PR_NUMBER", "PR_AUTHOR", "HEAD_SHA", "CRITIC_REVIEWER"]
    missing = [name for name in required if not env.get(name, "").strip()]
    if missing:
        print("::error::Missing required release-gate environment values: " + ", ".join(missing))
        return 1
    try:
        pr_number = int(env["PR_NUMBER"])
        blue_state = Path("AMX/ROOT/BLUE_STATE/BLUE_STATE_MANDATE_BINDING_AND_PREFLIGHT_V1.md").read_text(encoding="utf-8")
        mandate_sha = extract_critic_mandate_sha(blue_state)
        reviews = _fetch_reviews(
            env["GITHUB_REPOSITORY"],
            pr_number,
            env["GITHUB_TOKEN"],
            env.get("GITHUB_API_URL", "https://api.github.com"),
        )
        approved, message = evaluate_critic_reviews(
            reviews,
            critic_login=env["CRITIC_REVIEWER"],
            pr_author=env["PR_AUTHOR"],
            head_sha=env["HEAD_SHA"],
            mandate_sha=mandate_sha,
        )
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"::error::{exc}")
        return 1

    if not approved:
        print(f"::error::{message}")
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
