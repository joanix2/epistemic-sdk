from dataclasses import dataclass
from .term import Term

@dataclass(frozen=True)
class RewriteRule:
    """Directed (possibly nondeterministic) transition, distinct from equality."""
    source: Term
    target: Term
