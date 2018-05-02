import asyncio
from .utils import sha
from .engine import JsonEngine


class PyknowRT:
    """PyknowRT engine.

    Set up global sessions with rule and fact updaters given asyncrhonous
    iterators.

    Usage::

        await PyknowRT(**kwargs).run()

    Once stablished a session, you can wait upon changes on provided async
    iterators for rule updates and fact updates with the run() coroutine.
    """
    available_sessions = {}

    def __new__(cls, session_name, rule_executor, facts, rules):
        if session_name in PyknowRT.available_sessions:
            return PyknowRT.available_sessions[session_name]
        return super().__new__(cls)

    def __init__(self, session_name, rule_executor, facts, rules):
        """Set up.

        Arguments:

            session_name: Unique session name per engine.
            rule_executor: Rule executor to extract RHS methods from.
            facts: Fact async iterator. Changes will be updated from here
            rules: Rule async iterator. Changes will be updated from here

        Async iterators use the rethinkdb way. that is, the format::

            {'old_val': "old_value",
             'new_val': "new_value"}

        For rules, there is an extra "status" parameter, a 'consecuence'
        parameter and a 'rule' one::

            {'old_val': {
                'status': False,
                'consecuence': 'execute', +
                'rule': {'Rule':...},
            }
            'new_val': {
                'status': True,
                'consecuence': 'execute',
                'rule': {'Rule': ...}}}

        And for facts:

            {'old_val': {
                'type': 'FooFact',
                'foo': 'bar'},
             'new_val': {}}
        """
        if session_name not in PyknowRT.available_sessions:
            PyknowRT.available_sessions[session_name] = self

        self.session = session_name
        self.facts = []
        self.rules = {}
        self.rule_executor = rule_executor
        self.fact_asynciterator = facts
        self.rule_asynciterator = rules
        self.fact_positions = {}
        self._engine = None
        self.coros = asyncio.gather(self.rule_updater(), self.fact_updater())

    @property
    def engine(self):
        """Return a generated engine based on current rules if not available.

        This handles rules reloading the hard way, by recreating the engine.
        """
        if not self._engine:
            methods = {"rule_" + a: b for a, b in enumerate(self.rules)}
            methods['executor'] = self.rule_executor
            methods['_facts'] = self.facts
            self._engine = type(self.session, (JsonEngine, ), methods)()
            self._engine.reset()

        return self._engine

    async def rule_updater(self):
        """Rule updater.

        Reads upon async iterator and applies the changes to self.rules
        If a change has been recorded, schedule engine reloading.
        """
        async for change in self.rule_asynciterator:
            curr = change['new_val']

            if change['old_val']:
                self.rules.pop(sha(change['old_val']))

            self._engine = None

            if not curr or not curr['status']:
                continue

            self.rules[sha(change['new_val'])] = self.engine.lhs_from_json(
                curr['rule'])(self.engine.rhs_from_json(curr['consecuence']))

    async def fact_updater(self):
        """Fact updater.

        It  retracts old values and declares new ones.
        It also sets up values on self.facts, to deffact' them later.
        """
        async for change in self.fact_asynciterator:
            if change['old_val']:
                old_hash = sha(change['old_val'])
                self.engine.retract(self.fact_positions[old_hash][0])
                self.facts.pop(self.fact_positions[old_hash][1])

            if change['new_val']:
                new_hash = sha(change['new_val'])
                newfact = self.engine.fact_from_json(change['new_val'])
                position = self.engine.declare(newfact).__factid__
                self.fact_positions[new_hash] = position, len(self.facts)
                self.facts.append(newfact)

    async def run(self):
        await self.coros
