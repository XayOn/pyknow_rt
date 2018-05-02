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


def test_instance(fakeexecutor, fakeiter):
    from pyknow_rt import PyknowRT
    executor = fakeexecutor()
    real = PyknowRT('sess', executor, fakeiter(), fakeiter())
    engine = real.engine
    assert hasattr(engine, 'lhs_from_json')
    assert engine == real.engine


def test_sha():
    from pyknow_rt.utils import sha
    res = 'b2213295d564916f89a6a42455567c87c3f480fcd7a1c15e220f17d7169a790b'
    assert sha('foo') == res


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


@pytest.mark.asyncio
async def test_rule_updater(fakeiter, fakeexecutor):
    class FakeRuleIterator:
        rules = iter([
            {
                'new_val': {
                    'status': True,
                    'consecuence': 'execute',
                    'rule': {
                        'Rule': [{
                            'Number': {
                                'a': {
                                    'MATCH': 'a'
                                }
                            }
                        }]
                    }
                },
                'old_val': {}
            },
            {
                'old_val': {
                    'status': True,
                    'consecuence': 'execute',
                    'rule': {
                        'Rule': [{
                            'Number': {
                                'a': {
                                    'MATCH': 'a'
                                }
                            }
                        }]
                    }
                },
                'new_val': {}
            },
        ])

        async def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.rules)
            except StopIteration:
                raise StopAsyncIteration

    from pyknow_rt import PyknowRT
    executor = fakeexecutor()
    real = PyknowRT('sess', executor, fakeiter(), FakeRuleIterator())
    engine = real.engine
    assert hasattr(engine, 'lhs_from_json')
    assert engine == real.engine
    assert not real.rules
    await real.rule_updater()


@pytest.mark.asyncio
async def test_rule_updater_disabled(fakeiter, fakeexecutor):
    class FakeRuleIterator:
        rules = iter([
            {
                'new_val': {
                    'status': False,
                    'consecuence': 'execute',
                    'rule': {
                        'Rule': [{
                            'Number': {
                                'a': {
                                    'MATCH': 'a'
                                }
                            }
                        }]
                    }
                },
                'old_val': {}
            },
        ])

        async def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.rules)
            except StopIteration:
                raise StopAsyncIteration

    from pyknow_rt import PyknowRT
    executor = fakeexecutor()
    real = PyknowRT('sess', executor, fakeiter(), FakeRuleIterator())
    engine = real.engine
    assert hasattr(engine, 'lhs_from_json')
    await real.rule_updater()
    assert not real.rules


@pytest.mark.asyncio
async def test_rule_updater_enabled(fakeiter, fakeexecutor):
    class FakeRuleIterator:
        rules = iter([
            {
                'new_val': {
                    'status': True,
                    'consecuence': 'execute',
                    'rule': {
                        'Rule': [{
                            'Number': {
                                'a': {
                                    'MATCH': 'a'
                                }
                            }
                        }]
                    }
                },
                'old_val': {}
            },
        ])

        async def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.rules)
            except StopIteration:
                raise StopAsyncIteration

    from pyknow_rt import PyknowRT
    executor = fakeexecutor()
    real = PyknowRT('sess', executor, fakeiter(), FakeRuleIterator())
    engine = real.engine
    assert hasattr(engine, 'lhs_from_json')
    await real.rule_updater()
    assert real.rules


@pytest.mark.asyncio
async def test_fact_updater(fakeiter, fakeexecutor):
    class FakeFactIterator:
        facts = iter([
            {
                'new_val': {
                    'type': 'FooFact',
                    'foo': 'bar'
                },
                'old_val': {}
            },
        ])

        async def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.facts)
            except StopIteration:
                raise StopAsyncIteration

    from pyknow_rt import PyknowRT
    executor = fakeexecutor()
    real = PyknowRT('sess', executor, FakeFactIterator(), fakeiter())

    await real.fact_updater()
    assert dict(real.facts[0])['foo'] == 'bar'


@pytest.mark.asyncio
async def test_fact_updater_retract(fakeiter, fakeexecutor):
    class FakeFactIterator:
        facts = iter([
            {
                'new_val': {
                    'type': 'FooFact',
                    'foo': 'bar'
                },
                'old_val': {}
            },
            {
                'old_val': {
                    'type': 'FooFact',
                    'foo': 'bar'
                },
                'new_val': {}
            },
        ])

        async def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.facts)
            except StopIteration:
                raise StopAsyncIteration

    from pyknow_rt import PyknowRT
    executor = fakeexecutor()
    real = PyknowRT('sess', executor, FakeFactIterator(), fakeiter())

    await real.fact_updater()
    assert not real.facts
