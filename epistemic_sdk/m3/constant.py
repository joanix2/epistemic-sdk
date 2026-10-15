from dataclasses import dataclass

@dataclass(frozen=True)
class Constant:
    value: str | int | float | bool
    sort: str
