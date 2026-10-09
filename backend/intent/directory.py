from __future__ import annotations

import json
from pathlib import Path

from .models import CanonicalEntity, SearchScope


class CanonicalDirectory:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.entities: dict[str, CanonicalEntity] = {}
        self.aliases: dict[str, set[str]] = {}
        self.reload()

    @staticmethod
    def _norm(value: str) -> str:
        return " ".join(value.casefold().strip().split())

    def reload(self) -> None:
        self.entities = {}
        self.aliases = {}
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        for raw in payload.get("entities", []):
            entity = CanonicalEntity.model_validate(raw)
            if entity.entity_id in self.entities:
                raise ValueError(f"duplicate canonical entity_id: {entity.entity_id}")
            self.entities[entity.entity_id] = entity
            for term in {entity.canonical_name, *entity.aliases}:
                key = self._norm(term)
                if key:
                    self.aliases.setdefault(key, set()).add(entity.entity_id)

    def get(self, entity_id: str) -> CanonicalEntity | None:
        return self.entities.get(entity_id)

    def resolve_alias(self, raw: str, allowed_scopes: set[SearchScope]) -> list[CanonicalEntity]:
        ids = self.aliases.get(self._norm(raw), set())
        return [self.entities[i] for i in sorted(ids) if self.entities[i].visibility in allowed_scopes]

    def search(self, query: str, allowed_scopes: set[SearchScope], limit: int = 10) -> list[CanonicalEntity]:
        tokens = {t for t in self._norm(query).replace("/", " ").split() if len(t) > 1}
        ranked: list[tuple[float, CanonicalEntity]] = []
        for entity in self.entities.values():
            if entity.visibility not in allowed_scopes:
                continue
            haystack = self._norm(" ".join([
                entity.canonical_name, entity.description, *entity.aliases, *entity.capabilities,
            ]))
            score = 0.0 if not tokens else sum(1.0 for t in tokens if t in haystack) / len(tokens)
            if score > 0:
                ranked.append((score, entity))
        ranked.sort(key=lambda item: (-item[0], item[1].canonical_name))
        return [entity for _, entity in ranked[:limit]]

    def identity_conflicts(self, raw: str, allowed_scopes: set[SearchScope]) -> list[str]:
        matches = self.resolve_alias(raw, allowed_scopes)
        return [m.entity_id for m in matches] if len(matches) > 1 else []
