from backend.marketplace_money import SandboxMoneyAdapter


def test_sandbox_money_contract_never_moves_money():
    adapter=SandboxMoneyAdapter()
    ref=adapter.reserve("LST-1","C°BUYER",50000)
    assert ref.startswith("SBX-")
    assert adapter.moves_real_money is False
    assert adapter.release(ref,50000).money_moved is False
    assert adapter.hold(ref,"review").money_moved is False
    assert adapter.prepare_settlement(ref,1000000).money_moved is False
    description=adapter.describe()
    assert description["production_provider_connected"] is False
    assert description["custody"] is False
