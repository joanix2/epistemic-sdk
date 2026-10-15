"""Popper ILP engine: full inductive logic programming (optional dependency).

Optional dependency: Popper (https://github.com/logic-and-learning-lab/Popper),
which requires a SWI-Prolog runtime (>= 9.2) and is installed from source
(``pip install git+https://github.com/logic-and-learning-lab/Popper@main``). It
is imported lazily and dynamically, so ``epistemic_sdk`` stays importable
without it; constructing :class:`PopperILPEngine` raises a clear ``ImportError``
when Popper is absent.

Popper's interface is *file-based* (it reads examples, bias and background
knowledge from files and returns a Prolog program), which must be translated
back into the SDK's M3 ``Term``/``ProgramM1``. That translation is a separate,
still-open piece of work; this adapter exposes the same ``infer`` contract as
the stdlib synthesis engines and delegates to Popper when it is installed.
"""

import importlib
from collections.abc import Sequence
from typing import Any

from epistemic_sdk import Hypothesis, KnowledgeBase
from epistemic_sdk.beliefs.belief_graph import BeliefGraph
from epistemic_sdk.m1.program_m1 import ProgramM1


class PopperILPEngine:
    """Abduce hypotheses using the Popper ILP system (requires SWI-Prolog + Popper)."""

    def __init__(self) -> None:
        self._popper: Any = self._import_popper()

    @staticmethod
    def _import_popper() -> Any:
        try:
            return importlib.import_module("popper")
        except ImportError as exc:
            raise ImportError(
                "PopperILPEngine requires Popper (install from source: "
                "pip install git+https://github.com/logic-and-learning-lab/Popper@main), "
                "itself requiring SWI-Prolog >= 9.2"
            ) from exc

    def infer(
        self,
        graph: BeliefGraph[Any],
        knowledge: KnowledgeBase[ProgramM1],
    ) -> Sequence[Hypothesis]:
        raise NotImplementedError(
            "PopperILPEngine: the file-based Popper -> ProgramM1 translation is not "
            "wired yet. Popper reads examples/bias/background-knowledge from files and "
            "returns a Prolog program; the adapter must write those files from the "
            "belief graph and parse the learned program back into M3 terms."
        )
