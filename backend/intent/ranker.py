from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

from .models import CandidateInput, CandidateOutcome, EpistemicState, HiddenVariable, IntentCriterion, IntentHypothesis


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.casefold()) if len(t) > 1}


def text_relevance(query: str, candidate: CandidateInput) -> float:
    q = _tokens(query)
    if not q:
        return 0.0
    hay = _tokens(f"{candidate.title} {candidate.summary}")
    return len(q & hay) / len(q)


def _age_days(timestamp: str | None) -> float | None:
    if not timestamp:
        return None
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 86400.0)
    except ValueError:
        return None


def freshness_multiplier(candidate: CandidateInput, criteria: list[IntentCriterion]) -> float:
    time_sensitive = {"price_zar", "available_now", "status", "state", "stock"}
    if not any(c.key in time_sensitive for c in criteria):
        return 1.0
    age = _age_days(candidate.source_timestamp)
    if age is None:
        return 0.75
    if age <= 7:
        return 1.0
    if age <= 30:
        return 0.85
    if age <= 180:
        return 0.60
    return 0.35


def _preference_range(candidates: list[CandidateInput], key: str) -> tuple[float, float] | None:
    values = [_number(c.attributes.get(key)) for c in candidates]
    numeric = [v for v in values if v is not None]
    if not numeric:
        return None
    return min(numeric), max(numeric)


def criterion_utility(candidate: CandidateInput, criterion: IntentCriterion, all_candidates: list[CandidateInput]) -> float:
    actual = candidate.attributes.get(criterion.key)
    target = criterion.value
    if actual is None:
        return 0.0
    op = criterion.operator
    if op == "eq":
        if isinstance(target, (int, float)) and not isinstance(target, bool):
            a, b = _number(actual), _number(target)
            if a is None or b is None:
                return 0.0
            return max(0.0, 1.0 - abs(a - b) / max(abs(b), 1.0))
        return 1.0 if actual == target else 0.0
    if op == "gte":
        a, b = _number(actual), _number(target)
        return 1.0 if a is not None and b is not None and a >= b else 0.0
    if op == "lte":
        a, b = _number(actual), _number(target)
        return 1.0 if a is not None and b is not None and a <= b else 0.0
    if op == "contains":
        return 1.0 if str(target).casefold() in str(actual).casefold() else 0.0
    if op in {"prefer_high", "prefer_low"}:
        n = _number(actual)
        bounds = _preference_range(all_candidates, criterion.key)
        if n is None or bounds is None:
            return 0.0
        lo, hi = bounds
        if hi <= lo:
            return 1.0
        scaled = (n - lo) / (hi - lo)
        return scaled if op == "prefer_high" else 1.0 - scaled
    return 0.0


def discover_hidden_variables(candidates: list[CandidateInput], measured_keys: set[str]) -> list[HiddenVariable]:
    values: dict[str, list[Any]] = {}
    ignored = {"status", "state", "title", "name"}
    for candidate in candidates:
        for key, value in candidate.attributes.items():
            if key in measured_keys or key in ignored:
                continue
            values.setdefault(key, []).append(value)
    hidden: list[HiddenVariable] = []
    for key, observed in values.items():
        unique = []
        seen = set()
        for value in observed:
            marker = repr(value)
            if marker not in seen:
                unique.append(value)
                seen.add(marker)
        if len(unique) <= 1:
            continue
        numeric = [_number(v) for v in unique]
        nums = [v for v in numeric if v is not None]
        if len(nums) >= 2:
            spread = (max(nums) - min(nums)) / max(abs(max(nums)), abs(min(nums)), 1.0)
            sensitivity = max(0.25, min(1.0, spread))
        else:
            sensitivity = min(1.0, 0.25 + 0.15 * len(unique))
        hidden.append(HiddenVariable(
            key=key,
            observed_values=unique[:8],
            decision_sensitivity=sensitivity,
            information_value=min(1.0, 0.45 + 0.1 * len(unique)),
            basis=[f"attribute varies across {len(observed)} candidate observations"],
        ))
    hidden.sort(key=lambda h: (-(h.decision_sensitivity * h.information_value), h.key))
    return hidden[:8]


def rank(
    candidates: list[CandidateInput],
    query: str,
    measured: list[IntentCriterion],
    hypotheses: list[IntentHypothesis],
) -> list[CandidateOutcome]:
    results: list[CandidateOutcome] = []
    measured_weight = sum(c.weight for c in measured) or 0.0
    active_hypotheses = [h for h in hypotheses if h.criterion is not None and h.probability > 0]
    total_hypothesis_probability = sum(h.probability for h in active_hypotheses) or 1.0

    for candidate in candidates:
        relevance = text_relevance(query, candidate)
        score_inputs: list[dict[str, Any]] = []
        measured_sum = 0.0
        decisive: list[str] = []
        for criterion in measured:
            utility = criterion_utility(candidate, criterion, candidates)
            measured_sum += utility * criterion.weight
            score_inputs.append({
                "layer": "MEASURED_INTENT",
                "key": criterion.key,
                "operator": criterion.operator,
                "target": criterion.value,
                "actual": candidate.attributes.get(criterion.key),
                "utility": round(utility, 6),
                "weight": criterion.weight,
                "epistemic_state": criterion.epistemic_state.value,
            })
            if utility >= 0.95:
                decisive.append(f"{criterion.key} satisfies {criterion.operator} {criterion.value!r}")

        measured_score = measured_sum / measured_weight if measured_weight else relevance
        if measured_weight:
            measured_score = 0.85 * measured_score + 0.15 * relevance
        fresh = freshness_multiplier(candidate, measured)
        measured_score *= fresh
        score_inputs.append({"layer": "FRESHNESS", "multiplier": fresh, "source_timestamp": candidate.source_timestamp})

        hypothesis_score = 0.0
        for hypothesis in active_hypotheses:
            utility = criterion_utility(candidate, hypothesis.criterion, candidates)
            contribution = utility * hypothesis.probability
            hypothesis_score += contribution
            score_inputs.append({
                "layer": "HYPOTHESIS",
                "hypothesis_id": hypothesis.hypothesis_id,
                "key": hypothesis.criterion.key,
                "utility": round(utility, 6),
                "probability": hypothesis.probability,
                "epistemic_state": hypothesis.epistemic_state.value,
            })
        hypothesis_score /= total_hypothesis_probability

        # Hypotheses can refine exploration but may never outrank the measured layer.
        eif = min(1.0, 0.80 * measured_score + 0.20 * hypothesis_score)
        pointers = [p for p in [candidate.evidence_pointer] if p]
        results.append(CandidateOutcome(
            candidate_id=candidate.candidate_id,
            title=candidate.title,
            summary=candidate.summary,
            entity_id=candidate.entity_id,
            entity_type=candidate.entity_type,
            attributes=candidate.attributes,
            measured_score=max(0.0, min(1.0, measured_score)),
            expected_intent_fulfilment=max(0.0, min(1.0, eif)),
            relevance_score=max(0.0, min(1.0, relevance)),
            score_inputs=score_inputs,
            evidence_pointers=pointers,
            decisive_factors=decisive[:4],
            action=candidate.action,
        ))

    results.sort(key=lambda c: (-c.measured_score, -c.expected_intent_fulfilment, -c.relevance_score, c.title.casefold()))
    return results


def expected_regret(ranked: list[CandidateOutcome], hypotheses: list[IntentHypothesis], hidden_variables: list[HiddenVariable] | None = None) -> float:
    if not ranked:
        return 1.0
    if len(ranked) == 1:
        margin_risk = 0.10
    else:
        margin = max(0.0, ranked[0].measured_score - ranked[1].measured_score)
        margin_risk = max(0.0, 0.50 - margin)
    active_hypotheses = [h for h in hypotheses if h.epistemic_state == EpistemicState.HYPOTHESIZED]
    hypothesis_risk = max((h.investigation_priority for h in active_hypotheses), default=0.0)
    # If a live hypothesis would favour a different candidate strongly enough to flip the winner,
    # regret must reflect that decision sensitivity rather than hide behind the current measured margin.
    if ranked and active_hypotheses:
        primary_id = ranked[0].candidate_id
        for hypothesis in active_hypotheses:
            utilities = []
            for candidate in ranked:
                for item in candidate.score_inputs:
                    if item.get("layer") == "HYPOTHESIS" and item.get("hypothesis_id") == hypothesis.hypothesis_id:
                        utilities.append((float(item.get("utility", 0.0)), candidate.candidate_id))
            if utilities:
                utilities.sort(reverse=True)
                best_utility, best_candidate = utilities[0]
                primary_utility = next((u for u, cid in utilities if cid == primary_id), 0.0)
                if best_candidate != primary_id and best_utility - primary_utility >= 0.35:
                    hypothesis_risk = max(hypothesis_risk, 0.75)
    hidden_risk = max((h.decision_sensitivity * h.information_value for h in (hidden_variables or [])), default=0.0)
    return max(0.0, min(1.0, 0.45 * margin_risk + 0.45 * hypothesis_risk + 0.10 * hidden_risk))
