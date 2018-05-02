import asyncio
from .utils import sha
from pyknow import Rule
from .engine import JsonEngine


class PyknowRT:
    def __init__(self, session_name, rule_executor, facts, rules):
        self.facts = []
        self.rules = {}
        self.rule_executor = rule_executor
        self.fact_asynciterator = facts
        self.rule_asynciterator = rules
        self.session = session_name
        self._engine = None

    async def rule_updater(self):
        async for change in self.rule_asynciterator:
            current = change['new_val']
            if not current['status']:
                continue

            lhs = self.lhs_from_json(current['rule'])
            rhs = self.rhs_from_json(current['consecuence'],
                                     self.rule_executor)

            if change['old_val']:
                self.rules.pop(sha(current['rule']['old_val']))

            self.rules[sha(change['new_val'])] = Rule(**lhs)(rhs)
            self.recreate_engine()
            self._engine = None

    @property
    def engine(self):
        if not self._engine:
            methods = {"rule_" + a: b for a, b in enumerate(self.rules)}
            self._engine = type(self.session, (JsonEngine, ), methods)

        return self._engine

    async def fact_updater(self):
        async for change in self.fact_asynciterator:
            if change['old_val']:
                self.engine.retract(**change['old_val'])
            self.engine.declare(**change['new_val'])


def get_engine(session_name):
    kengine = PyknowRT()
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(kengine.rule_updater(), kengine.fact_updater()))
