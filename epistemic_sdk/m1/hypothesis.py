from dataclasses import dataclass

from .inference_mode import InferenceMode
from .program_m1 import ProgramM1


@dataclass(frozen=True)
class Hypothesis:
    """An M1 declarative program proposed for empirical/formal checking."""
    id: str
    program: ProgramM1
    supporting_belief_ids: tuple[str, ...] = ()
    inference_mode: InferenceMode = InferenceMode.ABDUCTION
