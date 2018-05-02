import pytest


def test_fact_from_json():
    from pyknow_rt import JsonEngine
    fact = {'type': 'fact_ex', 'foo': 'bar'}
    fact = JsonEngine().fact_from_json(fact)
    assert fact.__class__.__name__ == 'fact_ex'


def test_getfacts():
    from pyknow_rt import JsonEngine
    facts = [{"type": "foo", "bar": "baz"}, {"type": "bar", "stuff": "stuff"}]
    facts2 = [{"type": "foo", "bar": "baz"}, {"type": "bar", "stuff": "stuff"}]
    engine = JsonEngine()
    engine._facts = facts
    assert list(engine.getfacts()) == [
        engine.fact_from_json(facts2[0]),
        engine.fact_from_json(facts2[1])
    ]


@pytest.mark.asyncio
async def test_rhs_from_json(fakeexecutor, testjson):
    """Test lhs from json."""
    from pyknow_rt import JsonEngine
    FakeExecutor = fakeexecutor()
    engine = type("engine", (JsonEngine, ), {"executor": FakeExecutor})()
    engine.rhs_from_json(testjson['new_val']['consecuence'])()
    assert FakeExecutor.executed


def test_pyknowdecoder(fakeexecutor):
    import operator
    from pyknow_rt import JsonEngine
    from pyknow_rt.utils import FactTypes
    from pyknow import Rule, TEST, MATCH
    executor = fakeexecutor()
    extra = {
        'Rule': [{
            'Number': {
                'a': {
                    'MATCH': 'a'
                }
            }
        }, {
            'Number': {
                'b': {
                    'MATCH': 'b'
                }
            }
        }, {
            'TEST': ['gt']
        }, {
            'Number': {
                'c': {
                    'MATCH': 'c'
                }
            }
        }, {
            'TEST': ['gt']
        }]
    }
    engine = type("engine", (JsonEngine, ), {"executor": executor})()
    res = engine.lhs_from_json(extra)
    Number = FactTypes.get('Number')
    expected = Rule(
        Number(a=MATCH.a),
        Number(b=MATCH.b),
        TEST(operator.gt),
        Number(c=MATCH.c),
        TEST(operator.gt))

    assert res == expected
