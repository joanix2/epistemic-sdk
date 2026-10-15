from dataclasses import dataclass

@dataclass(frozen=True)
class Operator:
    """Operator declaration: argument sort names -> result sort name."""
    name: str
    arguments: tuple[str, ...]
    result: str
