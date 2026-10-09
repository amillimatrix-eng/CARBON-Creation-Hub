from __future__ import annotations

from pathlib import Path
from typing import Callable
from uuid import uuid4

from .claims import contradiction_groups, normalize_candidate_claims
from .directory import CanonicalDirectory
from .interpreter import DeterministicIntentInterpreter, IntentProvider
from .models import (
    ActionRequest,
    CandidateInput,
    CandidateOutcome,
    ContextSignal,
    EpistemicState,
    FeedbackRequest,
    IntentCriterion,
    IntentHypothesis,
    IntentPivot,
    PivotRequest,
    SearchIntentRequest,
    SearchResponse,
    SearchScope,
    SearchSession,
    SearchStatus,
)
from .ranker import discover_hidden_variables, expected_regret, rank
from .store import SearchSessionStore, utcnow

CandidateSearch = Callable[[str, int], list[CandidateInput]]


class SearchEngine:
    def __init__(
        self,
        root: Path,
        session_store: SearchSessionStore,
        directory: CanonicalDirectory,
        intent_provider: IntentProvider | None = None,
        evidence_search: CandidateSearch | None = None,
        external_search: CandidateSearch | None = None,
        marketplace_search: CandidateSearch | None = None,
    ):
        self.root = Path(root)
        self.sessions = session_store
        self.directory = directory
        self.interpreter = intent_provider or DeterministicIntentInterpreter()
        self.evidence_search = evidence_search
        self.external_search = external_search
        self.marketplace_search = marketplace_search

    def _directory_candidates(self, query: str, allowed: set[SearchScope], limit: int) -> list[CandidateInput]:
        out: list[CandidateInput] = []
        for entity in self.directory.search(query, allowed, limit):
            out.append(CandidateInput(
                candidate_id=f"dir:{entity.entity_id}",
                title=entity.canonical_name,
                summary=entity.description,
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                attributes={"capabilities": entity.capabilities, "lifecycle_state": entity.lifecycle_state},
                source=entity.authoritative_source or "canonical_directory",
                source_type="CANONICAL_DIRECTORY",
                visibility=entity.visibility,
                evidence_pointer=entity.evidence_pointer,
                action={"name": entity.offered_actions[0]} if entity.offered_actions else None,
            ))
        return out

    @staticmethod
    def _dedupe(candidates: list[CandidateInput]) -> list[CandidateInput]:
        seen: set[tuple[str, str]] = set()
        out: list[CandidateInput] = []
        for candidate in candidates:
            key = (candidate.entity_id or "", candidate.candidate_id)
            if key in seen:
                continue
            seen.add(key)
            out.append(candidate)
        return out

    @staticmethod
    def _visible_candidates(candidates: list[CandidateInput], allowed: set[SearchScope]) -> list[CandidateInput]:
        return [candidate for candidate in candidates if candidate.visibility in allowed]

    @staticmethod
    def _assert_context_scope(signals: list[ContextSignal], allowed: set[SearchScope]) -> None:
        illegal = [s.visibility.value for s in signals if s.visibility not in allowed]
        if illegal:
            raise PermissionError("context signal visibility is not authorized")

    def _pivots(self, hypotheses: list[IntentHypothesis], ranked: list[CandidateOutcome], max_pivots: int) -> list[IntentPivot]:
        pivots: list[IntentPivot] = []
        for hyp in sorted(hypotheses, key=lambda h: -h.investigation_priority):
            if hyp.epistemic_state != EpistemicState.HYPOTHESIZED or not hyp.criterion:
                continue
            projected = next((c.candidate_id for c in ranked if hyp.criterion.key in c.attributes), None)
            label = "Want to test " + hyp.label.rstrip("?.") + "?"
            if hyp.hypothesis_id == "ram-physical-split":
                label = "Want more physical RAM?"
            pivots.append(IntentPivot(
                pivot_id=f"pivot:{hyp.hypothesis_id}",
                label=label,
                hypothesis_id=hyp.hypothesis_id,
                reason="Optional hypothesis test; not asserted as user preference.",
                projected_candidate_id=projected,
            ))
            if len(pivots) >= max_pivots:
                break
        return pivots

    @staticmethod
    def _preserved_inputs(session: SearchSession) -> list[CandidateInput]:
        return [
            CandidateInput(
                candidate_id=c.candidate_id,
                title=c.title,
                summary=c.summary,
                entity_id=c.entity_id,
                entity_type=c.entity_type,
                attributes=c.attributes,
                source="preserved_session",
                source_type="SESSION",
                visibility=SearchScope.PUBLIC if SearchScope.PUBLIC in session.allowed_scopes else session.allowed_scopes[0],
                evidence_pointer=c.evidence_pointers[0] if c.evidence_pointers else None,
                action=c.action,
            )
            for c in session.candidates
        ]

    def _recompute(self, session: SearchSession, reason: str) -> None:
        preserved = self._preserved_inputs(session)
        ranked = rank(preserved, session.raw_query, session.measured_intent, session.hypotheses)
        session.candidates = ranked
        session.primary = ranked[0] if ranked else None
        session.hidden_variables = discover_hidden_variables(preserved, {c.key for c in session.measured_intent})
        session.confidence = ranked[0].expected_intent_fulfilment if ranked else 0.0
        session.expected_regret = expected_regret(ranked, session.hypotheses, session.hidden_variables)
        session.decision_stable = bool(ranked) and session.expected_regret <= 0.45 and not session.contradictions
        session.status = SearchStatus.RESOLVED if ranked else SearchStatus.HOLD
        session.stop_reason = reason
        session.updated_at = utcnow()

    def search(self, request: SearchIntentRequest, allowed_scopes: set[SearchScope]) -> SearchResponse:
        requested = set(request.requested_scopes)
        if not requested.issubset(allowed_scopes):
            raise PermissionError("requested search scope is not authorized")
        self._assert_context_scope(request.context_signals, allowed_scopes)

        interp = self.interpreter.interpret(request)
        measured = [c for c in interp.criteria if c.epistemic_state in {EpistemicState.EXPLICIT, EpistemicState.MEASURED}]
        candidates = self._visible_candidates(list(request.candidates), allowed_scopes)
        candidates += self._directory_candidates(request.query, allowed_scopes, request.limit)

        provider_state = "LOCAL_RULES"
        if self.evidence_search and requested & {SearchScope.PUBLIC, SearchScope.CARBON_INTERNAL}:
            candidates += self._visible_candidates(self.evidence_search(request.query, request.limit), allowed_scopes)

        if SearchScope.CARBON_MARKETPLACE in requested:
            if self.marketplace_search:
                candidates += self._visible_candidates(self.marketplace_search(request.query, request.limit), allowed_scopes)
                provider_state = "MARKETPLACE_ADAPTER_OK"
            else:
                provider_state = "MARKETPLACE_ADAPTER_UNRESOLVED"

        external_required = request.provider_mode == "EXTERNAL"
        if SearchScope.EXTERNAL_WEB in requested:
            if self.external_search:
                try:
                    candidates += self._visible_candidates(self.external_search(request.query, request.limit), allowed_scopes)
                    provider_state = "EXTERNAL_PROVIDER_OK"
                except Exception:
                    provider_state = "INTENT_ENGINE_UNAVAILABLE" if external_required else "EXTERNAL_PROVIDER_DEGRADED"
            elif external_required:
                provider_state = "INTENT_ENGINE_EXTERNAL_UNAVAILABLE"

        candidates = self._dedupe(candidates)
        raw_claims = [claim for c in candidates for claim in normalize_candidate_claims(c)]
        claims, contradictions = contradiction_groups(raw_claims)
        hidden_variables = discover_hidden_variables(candidates, {c.key for c in measured})
        ranked = rank(candidates, request.query, measured, interp.hypotheses)[:request.limit]
        regret = expected_regret(ranked, interp.hypotheses, hidden_variables)

        material_gaps: list[str] = []
        identity_conflicts = self.directory.identity_conflicts(request.query, allowed_scopes)
        if identity_conflicts:
            material_gaps.append("Ambiguous canonical identity: " + ", ".join(identity_conflicts))
        if contradictions:
            material_gaps.append("Unresolved contradictory claims exist for a candidate attribute.")
        if external_required and provider_state != "EXTERNAL_PROVIDER_OK":
            material_gaps.append("Authorized external retrieval provider is required.")

        if external_required and provider_state != "EXTERNAL_PROVIDER_OK":
            status = SearchStatus.HOLD
            stop_reason = "External retrieval is required but unavailable. HOLD rather than silently downgrade."
        elif not ranked:
            status = SearchStatus.HOLD
            stop_reason = "No defensible candidate was retrieved. HOLD/GET_EVIDENCE."
            material_gaps.append("No candidate evidence.")
        else:
            status = SearchStatus.RESOLVED
            stop_reason = "Defensible primary resolution produced from measured evidence; optional pivots remain hypotheses."

        confidence = ranked[0].expected_intent_fulfilment if ranked else 0.0
        decision_stable = bool(ranked) and regret <= 0.45 and not contradictions and not material_gaps
        if ranked and not decision_stable:
            stop_reason = "Primary resolution available, but Expected Regret or unresolved evidence keeps the decision open."

        pivots = self._pivots(interp.hypotheses, ranked, request.max_pivots) if request.allow_pivots and ranked else []
        now = utcnow()
        session_id = "SRC-" + uuid4().hex.upper()
        session = SearchSession(
            session_id=session_id,
            status=status,
            raw_query=request.query,
            surface=request.surface,
            allowed_scopes=sorted(allowed_scopes, key=lambda s: s.value),
            observed_signals=interp.observed_signals,
            explicit_constraints=interp.criteria,
            measured_intent=measured,
            hypotheses=interp.hypotheses,
            hidden_variables=hidden_variables,
            negative_signals=interp.negative_signals,
            candidates=ranked,
            claims=claims,
            contradictions=contradictions,
            primary=ranked[0] if ranked else None,
            pivots=pivots,
            confidence=confidence,
            expected_regret=regret,
            decision_stable=decision_stable,
            stop_reason=stop_reason,
            material_gaps=material_gaps,
            provider_state=provider_state,
            created_at=now,
            updated_at=now,
            audit_ref=f"search://{session_id}",
        )
        self.sessions.save(session, "SEARCH_CREATED", {
            "query": request.query,
            "surface": request.surface,
            "scopes": [s.value for s in requested],
            "candidate_count": len(ranked),
            "claim_count": len(claims),
            "contradiction_count": len(contradictions),
            "provider_state": provider_state,
            "intent_snapshot": [c.model_dump(mode="json") for c in measured],
            "stop_reason": stop_reason,
            "primary_id": session.primary.candidate_id if session.primary else None,
        })
        return self._response(session)

    def get_session(self, session_id: str) -> SearchSession | None:
        return self.sessions.get(session_id)

    def pivot(self, session_id: str, request: PivotRequest) -> SearchResponse:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError("search session not found")
        pivot = next((p for p in session.pivots if p.pivot_id == request.pivot_id), None)
        if not pivot:
            raise KeyError("intent pivot not found")
        hypothesis = next((h for h in session.hypotheses if h.hypothesis_id == pivot.hypothesis_id), None)
        if not hypothesis or not hypothesis.criterion:
            raise ValueError("pivot has no testable criterion")

        promoted = hypothesis.criterion.model_copy(deep=True)
        promoted.epistemic_state = EpistemicState.EXPLICIT
        promoted.signal_basis = [f"user selected pivot: {pivot.label}"]
        session.measured_intent = [c for c in session.measured_intent if c.key != promoted.key] + [promoted]
        hypothesis.epistemic_state = EpistemicState.MEASURED
        session.selected_pivot = pivot.pivot_id
        self._recompute(session, "Intent pivot selected; preserved evidence reweighted in the same session.")
        self.sessions.save(session, "INTENT_PIVOT_SELECTED", {
            "pivot_id": pivot.pivot_id,
            "hypothesis_id": hypothesis.hypothesis_id,
            "rollback_boundary": "DERIVED_RANKING_AND_STOP_STATE",
            "evidence_preserved": True,
        })
        return self._response(session)

    def feedback(self, session_id: str, request: FeedbackRequest) -> SearchResponse:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError("search session not found")

        if request.kind == "CORRECT":
            session.correction_count += 1
            if request.signal:
                if request.signal.visibility not in set(session.allowed_scopes):
                    raise PermissionError("correction signal visibility is not authorized")
                session.observed_signals.append(request.signal)
                if request.signal.signal_type in {"criterion", "preference", "constraint"} and isinstance(request.signal.value, dict) and request.signal.value.get("key"):
                    criterion = IntentCriterion(
                        key=str(request.signal.value["key"]),
                        operator=request.signal.value.get("operator", "eq"),
                        value=request.signal.value.get("value"),
                        weight=float(request.signal.value.get("weight", 1.0)),
                        epistemic_state=EpistemicState.MEASURED,
                        signal_basis=[request.signal.provenance or request.signal.source],
                    )
                    session.measured_intent = [c for c in session.measured_intent if c.key != criterion.key] + [criterion]
                if request.signal.signal_type in {"reject", "negative"}:
                    session.negative_signals.append(str(request.signal.value))
            self._recompute(session, "Correction applied; dependent ranking/stop state reweighted while evidence/session continuity was preserved.")
            event = {
                "message": request.message,
                "rollback_boundary": "DERIVED_INTERPRETATION_RANKING_STOP_STATE",
                "preserved_evidence": True,
                "measured_intent_count": len(session.measured_intent),
            }
        else:
            if session.primary:
                calibration = self.sessions.record_feedback(
                    f"outcome:{session.primary.entity_id or session.primary.candidate_id}",
                    positive=request.kind == "CONFIRM",
                )
            else:
                calibration = None
            session.stop_reason = f"{request.kind} feedback recorded for versioned calibration; historical evidence is unchanged."
            session.updated_at = utcnow()
            event = {"message": request.message, "calibration": calibration, "preserved_evidence": True}

        self.sessions.save(session, f"FEEDBACK_{request.kind}", event)
        return self._response(session)

    def action(self, session_id: str, request: ActionRequest) -> dict:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError("search session not found")
        candidate = next((c for c in session.candidates if c.candidate_id == request.candidate_id), None) if request.candidate_id else session.primary
        if not candidate or not candidate.action:
            raise PermissionError("candidate has no authorized action")
        if candidate.action.get("name") != request.action:
            raise PermissionError("requested action is not authorized for this candidate")
        session.action_state = {"action": request.action, "candidate_id": candidate.candidate_id, "binding": False}
        session.updated_at = utcnow()
        self.sessions.save(session, "ACTION_ROUTED", session.action_state)
        return session.action_state

    def evidence(self, session_id: str) -> dict:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError("search session not found")
        return {
            "session_id": session_id,
            "contract_version": session.contract_version,
            "claims": [c.model_dump(mode="json") for c in session.claims],
            "contradictions": session.contradictions,
            "events": self.sessions.events(session_id),
            "calibration": self.sessions.calibration(),
        }

    @staticmethod
    def _response(session: SearchSession) -> SearchResponse:
        return SearchResponse(
            session_id=session.session_id,
            status=session.status,
            measured_intent=session.measured_intent,
            hypotheses=session.hypotheses,
            hidden_variables=session.hidden_variables,
            primary=session.primary,
            pivots=session.pivots,
            confidence=session.confidence,
            expected_regret=session.expected_regret,
            decision_stable=session.decision_stable,
            stop_reason=session.stop_reason,
            material_gaps=session.material_gaps,
            provider_state=session.provider_state,
            audit_ref=session.audit_ref,
        )
