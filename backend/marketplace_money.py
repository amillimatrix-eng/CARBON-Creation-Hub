from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class MoneyInstruction:
    provider_ref: str
    state: str
    amount_minor: int | None = None
    money_moved: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


class MoneyAdapter(Protocol):
    """CARBON°'s regulated-money seam.

    Product logic may request money operations through this contract, but no
    product state should assume that a request is legally or financially final
    until the configured provider returns an approved state.
    """

    name: str
    moves_real_money: bool

    def reserve(self, context_ref: str, buyer_ref: str, amount_minor: int) -> MoneyInstruction: ...
    def release(self, provider_ref: str, amount_minor: int | None = None) -> MoneyInstruction: ...
    def hold(self, provider_ref: str, reason: str) -> MoneyInstruction: ...
    def prepare_settlement(self, provider_ref: str, amount_minor: int) -> MoneyInstruction: ...
    def describe(self) -> dict: ...


class SandboxMoneyAdapter:
    """Development-only adapter. It never touches a financial rail."""

    name = "SANDBOX_NO_MONEY_MOVED"
    moves_real_money = False

    def reserve(self, context_ref: str, buyer_ref: str, amount_minor: int) -> MoneyInstruction:
        material = f"{context_ref}:{buyer_ref}:{amount_minor}:{uuid4().hex}"
        provider_ref = "SBX-" + hashlib.sha256(material.encode()).hexdigest()[:24].upper()
        return MoneyInstruction(provider_ref, "SANDBOX_RESERVED", amount_minor, False)

    def release(self, provider_ref: str, amount_minor: int | None = None) -> MoneyInstruction:
        return MoneyInstruction(provider_ref, "SANDBOX_RELEASE_PENDING", amount_minor, False)

    def hold(self, provider_ref: str, reason: str) -> MoneyInstruction:
        del reason
        return MoneyInstruction(provider_ref, "SANDBOX_HOLD", None, False)

    def prepare_settlement(self, provider_ref: str, amount_minor: int) -> MoneyInstruction:
        return MoneyInstruction(provider_ref, "SANDBOX_READY_FOR_PROVIDER", amount_minor, False)

    def describe(self) -> dict:
        return {
            "name": self.name,
            "moves_real_money": False,
            "custody": False,
            "reserve": "simulated",
            "release": "simulated",
            "hold": "simulated",
            "settlement": "simulated",
            "production_provider_connected": False,
        }
