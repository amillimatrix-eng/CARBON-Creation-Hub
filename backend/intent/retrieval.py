from __future__ import annotations

from typing import Protocol

from .models import CandidateInput, SearchScope


class RetrievalAdapter(Protocol):
    name: str

    def search(self, query: str, limit: int, allowed_scopes: set[SearchScope]) -> list[CandidateInput]: ...


class ExternalRetrievalAdapter(Protocol):
    name: str

    def search(self, query: str, limit: int) -> list[CandidateInput]: ...
