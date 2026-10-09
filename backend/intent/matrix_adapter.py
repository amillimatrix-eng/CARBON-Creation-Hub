from __future__ import annotations

from typing import Any, Callable

from .models import ContextSignal, SearchIntentRequest, SearchResponse, SearchScope


class MatrixSearchAdapter:
    """Thin Matrix caller adapter. Requested scope never becomes granted authority."""

    def __init__(
        self,
        invoke: Callable[[SearchIntentRequest, set[SearchScope]], SearchResponse],
        authorized_scopes: set[SearchScope] | None = None,
    ):
        self._invoke = invoke
        self._authorized_scopes = authorized_scopes or {
            SearchScope.PUBLIC, SearchScope.MATRIX_INTERNAL, SearchScope.CARBON_INTERNAL,
        }

    def search(
        self,
        query: str,
        *,
        scopes: list[SearchScope] | None = None,
        context: list[dict[str, Any]] | None = None,
    ) -> SearchResponse:
        requested = set(scopes or [SearchScope.PUBLIC])
        if not requested.issubset(self._authorized_scopes):
            raise PermissionError("Matrix Search request exceeds caller authority")
        request = SearchIntentRequest(
            query=query,
            surface="matrix",
            requested_scopes=list(requested),
            context_signals=[ContextSignal.model_validate(item) for item in (context or [])],
        )
        return self._invoke(request, set(self._authorized_scopes))
