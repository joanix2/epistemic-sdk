from dataclasses import dataclass

from .term import Term


@dataclass(frozen=True)
class Membership:
    """Membership of a term in a sort."""
    term: Term
    sort: str
