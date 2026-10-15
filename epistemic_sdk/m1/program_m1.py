from dataclasses import dataclass
from epistemic_sdk.m3.term import Term
from epistemic_sdk.m3.rewrite_rule import RewriteRule

@dataclass(frozen=True)
class ProgramM1:
    """Hypothetical program in a specific M2 language version.

    Candidate rules are NOT promoted to axioms merely by being executed.
    """
    language_id: str
    language_version: str
    entrypoint: Term
    candidate_rules: tuple[RewriteRule, ...] = ()
