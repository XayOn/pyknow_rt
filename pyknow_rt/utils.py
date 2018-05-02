import json
from hashlib import sha256
from pyknow import Fact


def sha(what):
    """Sha hash."""
    hasher = sha256()
    hasher.update(json.dumps(what).encode())
    return hasher.hexdigest()


class FactTypes:
    """Fact types."""
    facts = {}

    @classmethod
    def get(cls, what):
        """Get fact."""
        if what not in cls.facts:
            cls.facts[what] = type(what, (Fact, ), {})
        return cls.facts[what]
