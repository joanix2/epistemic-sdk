"""Algorithm registry: the epistemic SDK's "library of algorithms".

The registry is the single point that knows the inventory of concrete algorithm
implementations. Entries are keyed by epistemic *function* (category), not by
the technical port they satisfy: one picks an algorithm by need ("abduction",
"validation", ...) rather than by interface. The port an implementation
satisfies is context, not a lookup key.

Canonical categories mirror the epistemic loop's functions:

* ``abduction``, ``induction``, ``deduction`` — logical inference (`InferenceMode`)
* ``optimization`` — search over the program space
* ``validation`` — confrontation with observations
* ``rewriting`` — program normalization
* ``execution`` — program evaluation
* ``assimilation`` — observation -> beliefs
* ``revision`` — knowledge-base update
"""

from typing import Any


class AlgorithmRegistry:
    """Catalogue of implementations keyed by ``(category, key)``.

    Implementations are heterogeneous (rewriters, interpreters, validators,
    inference engines) and their concrete types are deliberately not unified
    behind a single interface. They are therefore stored as ``Any``; the caller
    recovers the concrete type by construction, since it registered the object
    under a known key. No type cast is needed at the registry boundary for the
    same reason.
    """

    def __init__(self) -> None:
        self._entries: dict[str, dict[str, Any]] = {}

    def register(self, category: str, key: str, implementation: Any) -> None:
        """Register ``implementation`` under ``(category, key)``.

        Re-registering an existing ``key`` overwrites it (last write wins).
        """
        self._entries.setdefault(category, {})[key] = implementation

    def pick(self, category: str, key: str) -> Any:
        """Return the implementation registered under ``(category, key)``.

        Raises :class:`KeyError` when the category or the key is unknown.
        """
        return self._entries[category][key]

    def get(self, category: str, key: str, default: Any = None) -> Any:
        """Like :meth:`pick`, but return ``default`` instead of raising."""
        return self._entries.get(category, {}).get(key, default)

    def categories(self) -> tuple[str, ...]:
        """Registered categories, in insertion order."""
        return tuple(self._entries)

    def keys(self, category: str) -> tuple[str, ...]:
        """Registered keys under ``category``, in insertion order."""
        return tuple(self._entries.get(category, {}))
