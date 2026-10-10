import json
import tempfile
import unittest
from pathlib import Path

from overdrive.forx_weighted_selector import run


# Real-data acceptance is intentionally coupled to the current durable buffer and ledger.\nclass LiveWeightedContinuityAcceptance(unittest.TestCase):
    def test_repository_real_outcomes_change_selection_and_persist(self):
        repo = Path(__file__).resolve().parents[1]
        buffer_path = repo / "overdrive" / "forx_prospect_buffer.json"
        opportunities_path = repo / "overdrive" / "opportunities.json"

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state1 = root / "state1.json"
            receipt1 = root / "receipt1.json"
            state2 = root / "state2.json"
            receipt2 = root / "receipt2.json"

            first = run(
                buffer_path,
                opportunities_path,
                None,
                state1,
                receipt1,
                5,
            )

            self.assertEqual(first["buffer_candidate_count"], 929)
            self.assertTrue(first["acceptance"]["three_outcome_classes_present"])
            self.assertTrue(first["acceptance"]["changed_next_selection"])
            self.assertTrue(first["acceptance"]["continuation_state_idempotent"])
            self.assertNotEqual(
                first["before_next_selection"],
                first["after_next_selection"],
            )

            second = run(
                buffer_path,
                opportunities_path,
                state1,
                state2,
                receipt2,
                5,
            )

            self.assertEqual(second["events_applied"], [])
            self.assertFalse(second["changed_next_selection"])
            self.assertEqual(
                json.loads(state1.read_text(encoding="utf-8")),
                json.loads(state2.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
