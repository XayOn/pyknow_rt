"""Test rules building."""
import pytest


@pytest.mark.asyncio
async def test_rhs_from_json(fakeexecutor, testjson):
    """Test lhs from json."""
    from pyknow_rt import JsonEngine
    FakeExecutor = fakeexecutor()
    engine = type("engine", (JsonEngine, ), {"executor": FakeExecutor})()
    engine.rhs_from_json(testjson['new_val']['consecuence'])()
    assert FakeExecutor.executed
