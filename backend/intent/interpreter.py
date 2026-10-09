from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from .models import ContextSignal, EpistemicState, IntentCriterion, IntentHypothesis, SearchIntentRequest


@dataclass(frozen=True)
class IntentInterpretation:
    criteria: list[IntentCriterion]
    hypotheses: list[IntentHypothesis]
    observed_signals: list[ContextSignal]
    negative_signals: list[str]


class IntentProvider(Protocol):
    def interpret(self, request: SearchIntentRequest) -> IntentInterpretation: ...


class DeterministicIntentInterpreter:
    """Bounded local interpreter. Detects signals; never fabricates preference."""

    _price = re.compile(r"(?:under|below|up to|about|around|roughly)?\s*(?:r|zar)\s*([0-9][0-9\s,.]*)", re.I)
    _ram = re.compile(r"(?<!\d)(\d{1,3})\s*(?:gb|g)\s*(?:ram)?", re.I)

    @staticmethod
    def _criterion_from_signal(signal: ContextSignal) -> IntentCriterion | None:
        if signal.signal_type not in {"criterion", "preference", "constraint"} or not isinstance(signal.value, dict):
            return None
        key = signal.value.get("key")
        if not key:
            return None
        return IntentCriterion(
            key=str(key),
            operator=signal.value.get("operator", "eq"),
            value=signal.value.get("value"),
            weight=float(signal.value.get("weight", 1.0)),
            epistemic_state=EpistemicState.MEASURED if signal.signal_type == "preference" else EpistemicState.EXPLICIT,
            signal_basis=[signal.provenance or signal.source],
        )

    def interpret(self, request: SearchIntentRequest) -> IntentInterpretation:
        criteria = [c.model_copy(deep=True) for c in request.criteria]
        hypotheses = [h.model_copy(deep=True) for h in request.hypotheses]
        observed = [s.model_copy(deep=True) for s in request.context_signals]
        negative: list[str] = []
        query = request.query.strip()
        q = query.casefold()
        observed.append(ContextSignal(signal_type="raw_query", value=query, source="query", confidence=1.0))

        for signal in request.context_signals:
            derived = self._criterion_from_signal(signal)
            if derived:
                criteria.append(derived)
            if signal.signal_type in {"reject", "negative"}:
                negative.append(str(signal.value))

        price = self._price.search(query)
        if price:
            raw = price.group(1).replace(" ", "").replace(",", "")
            try:
                value = float(raw)
                operator = "lte" if any(token in q for token in ("under", "below", "up to")) else "eq"
                criteria.append(IntentCriterion(
                    key="price_zar", operator=operator, value=value, weight=1.2,
                    epistemic_state=EpistemicState.EXPLICIT, signal_basis=[price.group(0).strip()],
                ))
            except ValueError:
                pass

        ram_match = self._ram.search(query)
        if ram_match and "ram" in q:
            amount = float(ram_match.group(1))
            explicit_physical = any(term in q for term in ("physical ram", "real ram", "hardware ram"))
            explicit_virtual = any(term in q for term in ("virtual ram", "extended ram", "memory expansion"))
            key = "physical_ram_gb" if explicit_physical else ("virtual_ram_gb" if explicit_virtual else "advertised_ram_gb")
            criteria.append(IntentCriterion(
                key=key, operator="eq", value=amount, weight=1.3 if explicit_physical else 1.0,
                epistemic_state=EpistemicState.EXPLICIT, signal_basis=[ram_match.group(0).strip()],
            ))
            if not explicit_physical and not explicit_virtual and not any(h.hypothesis_id == "ram-physical-split" for h in hypotheses):
                hypotheses.append(IntentHypothesis(
                    hypothesis_id="ram-physical-split",
                    label="more physical RAM may matter separately from advertised/virtual RAM",
                    probability=0.35,
                    signal_basis=["RAM was explicitly specified", "advertised RAM can combine physical and virtual memory"],
                    criterion=IntentCriterion(
                        key="physical_ram_gb", operator="prefer_high", value=None, weight=1.0,
                        epistemic_state=EpistemicState.HYPOTHESIZED,
                        signal_basis=["hidden-variable test only"],
                    ),
                    decision_impact=0.8, information_value=0.9, cost_of_error=0.6,
                ))

        if any(term in q for term in ("in stock", "available now", "order now", "available today")):
            criteria.append(IntentCriterion(
                key="available_now", operator="eq", value=True, weight=1.2,
                epistemic_state=EpistemicState.EXPLICIT, signal_basis=["availability wording in query"],
            ))

        if "not " in q or "don't" in q or "do not" in q:
            negative.append(query)

        seen: set[tuple[str, str, str]] = set()
        unique: list[IntentCriterion] = []
        for criterion in criteria:
            key = (criterion.key, criterion.operator, repr(criterion.value))
            if key not in seen:
                unique.append(criterion)
                seen.add(key)

        return IntentInterpretation(unique, hypotheses, observed, negative)
