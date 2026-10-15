from enum import Enum


class ValidationStatus(str, Enum):
    CORROBORATED = "corroborated"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
