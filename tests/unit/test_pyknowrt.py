import pytest


def test_instance(fakeexecutor, fakeiter):
    from pyknow_rt import PyknowRT
    executor = fakeexecutor()
    real = PyknowRT('sess', executor, fakeiter(), fakeiter())
    engine = real.engine
    assert hasattr(engine, 'lhs_from_json')
    assert engine == real.engine


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
