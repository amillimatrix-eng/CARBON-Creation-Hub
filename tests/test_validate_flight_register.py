import json
import unittest

from overdrive.forensics.validate_flight_register import git_blob_sha1, validate


def event(event_id, event_type, **extra):
    row = {
        "event_id": event_id,
        "event_type": event_type,
        "flight_id": "FLIGHT-1",
        "authorization_id": "AUTH-1",
        "status": "IN_FLIGHT",
        "recorded_at_utc": "2026-10-13T20:51:00Z",
    }
    row.update(extra)
    return row


def fixture(events, index_template):
    raw = ("\n".join(json.dumps(e, separators=(",", ":")) for e in events) + "\n").encode()
    return raw, index_template.replace("BLOB_SHA", git_blob_sha1(raw))


class FlightRegisterValidationTests(unittest.TestCase):
    def test_valid_checkpoint_with_later_landing_and_resume(self):
        events = [
            event("launch-1", "LAUNCH"),
            event("checkpoint-1", "CHECKPOINT", prior_event="launch-1"),
            event("landing-1", "LANDING", prior_event="checkpoint-1", status="LANDED_PARTIAL"),
            event("resume-1", "RESUME", prior_event="landing-1"),
        ]
        raw, index = fixture(
            events,
            "- **Latest continuity checkpoint:** event `checkpoint-1`, blob `BLOB_SHA`",
        )
        self.assertEqual(validate(raw, index), [])

    def test_index_cannot_claim_unregistered_flight(self):
        raw, index = fixture(
            [event("launch-1", "LAUNCH")],
            "- **Latest continuity checkpoint:** event `launch-1`, blob `BLOB_SHA`\n"
            "- **Existing flight:** `FORX-UNREGISTERED`, segment 04",
        )
        errors = validate(raw, index)
        self.assertTrue(any("FORX-UNREGISTERED" in error for error in errors))

    def test_stale_index_blob_fails(self):
        raw, index = fixture(
            [event("launch-1", "LAUNCH"), event("checkpoint-1", "CHECKPOINT")],
            "- **Latest continuity checkpoint:** event `checkpoint-1`, blob "
            "`0000000000000000000000000000000000000000`",
        )
        errors = validate(raw, index)
        self.assertTrue(any("blob pointer is stale" in error for error in errors))

    def test_missing_prior_event_fails_closed(self):
        raw, index = fixture(
            [
                event("launch-1", "LAUNCH"),
                event("checkpoint-1", "CHECKPOINT", prior_event="missing-resume"),
            ],
            "- **Latest continuity checkpoint:** event `checkpoint-1`, blob `BLOB_SHA`",
        )
        errors = validate(raw, index)
        self.assertTrue(any("prior_event 'missing-resume' is absent" in error for error in errors))

    def test_missing_prior_event_fails_closed(self):
        raw, index = fixture(
            [
                event("launch-1", "LAUNCH"),
                event("checkpoint-1", "CHECKPOINT", prior_event="missing-resume"),
            ],
            "- **Latest continuity checkpoint:** event `checkpoint-1`, blob `BLOB_SHA`",
        )
        errors = validate(raw, index)
        self.assertTrue(any("prior_event 'missing-resume' is absent" in error for error in errors))

    def test_duplicate_event_id_fails(self):
        raw, index = fixture(
            [event("launch-1", "LAUNCH"), event("launch-1", "CHECKPOINT")],
            "- **Latest continuity checkpoint:** event `launch-1`, blob `BLOB_SHA`",
        )
        errors = validate(raw, index)
        self.assertTrue(any("duplicate event_id" in error for error in errors))

    def test_flight_without_launch_fails_closed(self):
        raw, index = fixture(
            [event("checkpoint-1", "CHECKPOINT")],
            "- **Latest continuity checkpoint:** event `checkpoint-1`, blob `BLOB_SHA`",
        )
        errors = validate(raw, index)
        self.assertTrue(any("exactly one registered LAUNCH" in error for error in errors))

    def test_index_must_reference_latest_checkpoint_not_older_checkpoint(self):
        raw, index = fixture(
            [
                event("launch-1", "LAUNCH"),
                event("checkpoint-1", "CHECKPOINT"),
                event("checkpoint-2", "CHECKPOINT"),
                event("resume-1", "RESUME"),
            ],
            "- **Latest continuity checkpoint:** event `checkpoint-1`, blob `BLOB_SHA`",
        )
        errors = validate(raw, index)
        self.assertTrue(any("latest CHECKPOINT" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
