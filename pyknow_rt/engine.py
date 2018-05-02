import json

import pyknow
from pyknow import KnowledgeEngine, DefFacts

from .utils import FactTypes


class PyknowDecoder(json.JSONDecoder):
    executor = None

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        def extract():
            def has_children(value):
                return isinstance(value, dict) and any(
                    isinstance(a, dict) for a in value.values())

            if not any(isinstance(k, dict) for k in obj.values()):
                for key, value in obj.items():
                    if hasattr(pyknow, key) and isinstance(value, str):
                        yield getattr(getattr(pyknow, key), value)
                    elif hasattr(pyknow, key) and isinstance(value, list):
                        if not any(has_children(val) for val in value):
                            for nkey, val in enumerate(value):
                                if hasattr(self.executor, val):
                                    value[nkey] = getattr(self.executor, val)
                            yield getattr(pyknow, key)(*value)
                        else:
                            for keya, vala in enumerate(value):
                                if isinstance(vala, dict):
                                    for key_f, val_f in vala.items():
                                        value[keya] = FactTypes.get(key_f)(
                                            **val_f)
                            yield getattr(pyknow, key)(*value)
            else:
                # Rule
                pass

        result = list(extract())
        if len(result) == 1:
            return result[0]
        if not result:
            return obj
        return result


class JsonEngine(KnowledgeEngine):
    executor = None

    @DefFacts()
    def getfacts(self):
        for fact in self._facts:
            yield self.fact_from_json(fact)

    @classmethod
    def lhs_from_json(cls, lhs):
        """Format:

            @Rule(Number(MATCH.a), Number(MATCH.b), TEST(lambda a, b: a > b),
                  Number(MATCH.c), TEST(lambda b, c: b > c))

        Would translate to::

            {'Rule': [
                {'Number': {'a': {'MATCH': 'a'}},
                {'Number': {'b': {'MATCH': 'b'}}},
                {'TEST': {['executor.operator.test_gt']},
                {'Number': {'c': {'MATCH': 'c'}}},
                {'TEST': {'args': ['executor.operator.test_gt']}},
            ]}

        """
        return json.loads(
            json.dumps(lhs),
            cls=type('Decoder', (PyknowDecoder, ), {
                'executor': cls.executor
            }))

    @classmethod
    def rhs_from_json(cls, rhs):
        return getattr(cls.executor, rhs)

    def fact_from_json(self, fact):
        return FactTypes.get(fact.pop('type'))(**fact)
