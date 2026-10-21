from scripts.matrix_critic_release_gate import evaluate_critic_reviews, extract_critic_mandate_sha

CRITIC = "matrix-critic-bot"
AUTHOR = "feature-author"
HEAD = "a" * 40
MANDATE_SHA = "d" * 64
RECEIPT = "AMX/ROOT/INTAKE/CRITIC-RECEIPT.md"


def review(*, state="APPROVED", commit_id=HEAD, body=None, reviewer=CRITIC, submitted="2026-10-21T10:00:00Z", review_id=1):
    return {
        "id": review_id,
        "user": {"login": reviewer},
        "state": state,
        "commit_id": commit_id,
        "submitted_at": submitted,
        "body": body if body is not None else (
            "MATRIX-CRITIC-RESULT: APPROVE\n"
            "MATRIX-CRITIC-MANDATE: AMX-MANDATE-MATRIX-CRITIC-V1\n"
            f"MATRIX-CRITIC-MANDATE-SHA256: {MANDATE_SHA}\n"
            f"MATRIX-CRITIC-REVIEWED-HEAD: {HEAD}\n"
            f"MATRIX-CRITIC-RECEIPT: {RECEIPT}\n"
        ),
    }


def test_approval_must_be_independent_exact_head_and_receipted():
    ok, _ = evaluate_critic_reviews([review()], critic_login=CRITIC, pr_author=AUTHOR, head_sha=HEAD, mandate_sha=MANDATE_SHA)
    assert ok


def test_missing_critic_is_fail_closed():
    ok, reason = evaluate_critic_reviews([], critic_login=CRITIC, pr_author=AUTHOR, head_sha=HEAD, mandate_sha=MANDATE_SHA)
    assert not ok
    assert "No review" in reason


def test_author_cannot_self_approve():
    ok, reason = evaluate_critic_reviews([review(reviewer=AUTHOR)], critic_login=AUTHOR, pr_author=AUTHOR, head_sha=HEAD, mandate_sha=MANDATE_SHA)
    assert not ok
    assert "self-approval" in reason


def test_stale_head_approval_is_rejected():
    ok, reason = evaluate_critic_reviews([review(commit_id="b" * 40)], critic_login=CRITIC, pr_author=AUTHOR, head_sha=HEAD, mandate_sha=MANDATE_SHA)
    assert not ok
    assert "exact current PR head" in reason


def test_latest_nonapproval_overrides_older_approval():
    reviews = [
        review(state="APPROVED", submitted="2026-10-21T10:00:00Z", review_id=1),
        review(state="CHANGES_REQUESTED", submitted="2026-10-21T11:00:00Z", review_id=2, body="Hold: the current evidence does not pass."),
    ]
    ok, reason = evaluate_critic_reviews(reviews, critic_login=CRITIC, pr_author=AUTHOR, head_sha=HEAD, mandate_sha=MANDATE_SHA)
    assert not ok
    assert "not APPROVED" in reason


def test_mismatched_mandate_or_missing_receipt_is_rejected():
    bad_body = (
        "MATRIX-CRITIC-RESULT: APPROVE\n"
        "MATRIX-CRITIC-MANDATE: AMX-MANDATE-MATRIX-CRITIC-V1\n"
        f"MATRIX-CRITIC-MANDATE-SHA256: {'e' * 64}\n"
        f"MATRIX-CRITIC-REVIEWED-HEAD: {HEAD}\n"
        "MATRIX-CRITIC-RECEIPT: TBD\n"
    )
    ok, _ = evaluate_critic_reviews([review(body=bad_body)], critic_login=CRITIC, pr_author=AUTHOR, head_sha=HEAD, mandate_sha=MANDATE_SHA)
    assert not ok


def test_current_blue_state_critic_digest_can_be_read():
    sample = (
        "## MATRIX CRITIC\n"
        f"**SHA-256:** `{MANDATE_SHA}`\n"
        "other mandate text\n"
        "## MATRIX COMMISSIONING INSPECTOR\n"
    )
    assert extract_critic_mandate_sha(sample) == MANDATE_SHA
