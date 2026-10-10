import json
import tempfile
import unittest
from pathlib import Path

from overdrive.forx_weighted_selector import apply_events, new_state, run, select

class WeightedContinuityTests(unittest.TestCase):
    def candidates(self):
        return [
            {"id":"SUPPORT-1","organization":"SupportCo","surface":"BPO customer service","outcome_space":["customer support","BPO"],"fit_note":""},
            {"id":"AI-1","organization":"AICo","surface":"Python AI engineering","outcome_space":["Python","AI evaluation"],"fit_note":""},
            {"id":"CREATIVE-1","organization":"DesignCo","surface":"brand design","outcome_space":["creative design"],"fit_note":""},
            {"id":"AI-2","organization":"AICo2","surface":"LLM evaluation","outcome_space":["LLM","AI QA"],"fit_note":""},
            {"id":"MARKET-1","organization":"MarketCo","surface":"merchant marketplace","outcome_space":["marketplace","seller"],"fit_note":""},
        ]

    def events(self):
        return [
            {"event_id":"r1","opportunity_key":"remote","state":"RESPONDED","family":"ai_engineering","observed_at":"2026-10-09","source_ids":["m1"]},
            {"event_id":"x1","opportunity_key":"saku","state":"REJECTED","family":"creative_design","observed_at":"2026-10-09","source_ids":["m2"]},
            {"event_id":"w1","opportunity_key":"mprtc","state":"WRONG_ROUTE","family":"recruitment_ops","observed_at":"2026-10-09","source_ids":["m3"]},
        ]

    def test_real_outcome_classes_change_next_selection(self):
        state = new_state()
        before = select(self.candidates(), state, 5)
        updated, applied = apply_events(state, self.events())
        after = select(self.candidates(), updated, 5)
        self.assertEqual(before[0]["id"], "SUPPORT-1")
        self.assertEqual(after[0]["id"], "AI-1")
        self.assertEqual({e["state"] for e in applied}, {"RESPONDED","REJECTED","WRONG_ROUTE"})
        self.assertEqual(updated["family_weights"]["ai_engineering"], 2.0)
        self.assertEqual(updated["family_weights"]["creative_design"], -1.0)
        self.assertEqual(updated["route_state"]["generic_wrong_route_events"], 1)

    def test_continuation_is_idempotent(self):
        first, applied1 = apply_events(new_state(), self.events())
        second, applied2 = apply_events(first, self.events())
        self.assertEqual(len(applied1), 3)
        self.assertEqual(applied2, [])
        self.assertEqual(first, second)

    def test_diversity_cap_survives_weighting(self):
        state, _ = apply_events(new_state(), self.events())
        selected = select(self.candidates(), state, 5)
        counts = {}
        for x in selected:
            counts[x["family"]] = counts.get(x["family"], 0) + 1
        self.assertTrue(all(v <= 2 for v in counts.values()))

    def test_hard_invalid_excluded_before_weighting(self):
        cands = self.candidates()
        cands.insert(0, {
            "id":"BAD-AI","organization":"Blocked","surface":"Python AI engineering",
            "outcome_space":["Python"],"fit_note":"Current listing excludes South Africa"
        })
        state, _ = apply_events(new_state(), self.events())
        self.assertNotIn("BAD-AI", [x["id"] for x in select(cands, state, 5)])

    def test_receipt_survives_continuation_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            buffer = root/"buffer.json"
            opps = root/"opps.json"
            state1 = root/"state1.json"
            receipt1 = root/"receipt1.json"
            state2 = root/"state2.json"
            receipt2 = root/"receipt2.json"
            buffer.write_text(json.dumps({"candidates": self.candidates()}), encoding="utf-8")
            opps.write_text(json.dumps({"records": {
                "remote": {"state":"RESPONDED","opportunity":"Agentic Systems Engineer","last_action_at":"2026-10-09","evidence":[{"source_id":"m1","observed_at":"2026-10-09"}]},
                "saku": {"state":"REJECTED","title":"Graphic Designer","last_action_at":"2026-10-09","evidence":[{"source_id":"m2","observed_at":"2026-10-09"}]},
                "mprtc": {"state":"WRONG_ROUTE","opportunity":"Recruitment conversion intelligence","last_action_at":"2026-10-09","evidence":[{"source_id":"m3","observed_at":"2026-10-09"}]},
            }}), encoding="utf-8")
            r1 = run(buffer, opps, None, state1, receipt1, 5)
            self.assertTrue(r1["changed_next_selection"])
            self.assertTrue(all(r1["acceptance"].values()))
            r2 = run(buffer, opps, state1, state2, receipt2, 5)
            self.assertEqual(r2["events_applied"], [])
            self.assertFalse(r2["changed_next_selection"])
            self.assertEqual(
                json.loads(state1.read_text(encoding="utf-8")),
                json.loads(state2.read_text(encoding="utf-8")),
            )

if __name__ == "__main__":
    unittest.main()
