from enum import Enum

class KnowledgeStatus(str, Enum):
    ACTIVE = "active"
    REFUTED = "refuted"
    SUPERSEDED = "superseded"
