import pytest
import operator


@pytest.fixture
def fakeexecutor():
    class FakeExecutor:
        executed = False

        def __getattr__(self, attr):
            if hasattr(operator, attr):
                return getattr(operator, attr)
            return super().__getattr__(attr)

        @staticmethod
        def execute():
            FakeExecutor.executed = True
            return

    return FakeExecutor


@pytest.fixture
def testjson():
    return {
        'new_val': {
            'rule': {},
            'consecuence': 'execute'
        },
        'old_val': {
            'rule': {},
            'consecuence': 'execute'
        }
    }


@pytest.fixture
def fakeiter():
    class Fake:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    return Fake
