"""Concrete M2 natural-number language and M1 candidate hypothesis.

Defines a theory, not a Maude runtime. Run: python -m examples.nat_language
"""
from epistemic_sdk import (
    Application,
    Axiom,
    Equation,
    Hypothesis,
    InferenceMode,
    LanguageM2,
    Operator,
    ProgramM1,
    RewriteRule,
    Sort,
    Variable,
)

X = Variable("X", "Nat")
Y = Variable("Y", "Nat")
ZERO = Application("zero", ())

def succ(t):
    return Application("succ", (t,))

def add(a, b):
    return Application("add", (a, b))

NAT = LanguageM2(
    id="nat", version="1.0.0", sorts=(Sort("Nat"),),
    operators=(
        Operator("zero", (), "Nat"),
        Operator("succ", ("Nat",), "Nat"),
        Operator("add", ("Nat", "Nat"), "Nat"),
    ),
    axioms=(
        Axiom("add_zero_left", Equation(add(ZERO, Y), Y), "definition"),
        Axiom(
            "add_successor",
            Equation(add(succ(X), Y), succ(add(X, Y))),
            "definition",
        ),
    ),
)

EXAMPLE = Hypothesis(
    id="H1",
    program=ProgramM1(
        language_id="nat", language_version="1.0.0",
        entrypoint=add(succ(ZERO), ZERO),
        candidate_rules=(RewriteRule(add(X, ZERO), X),),
    ),
    inference_mode=InferenceMode.INDUCTION,
)

if __name__ == "__main__":
    print(NAT)
    print(EXAMPLE)
