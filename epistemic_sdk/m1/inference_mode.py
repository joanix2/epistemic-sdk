from enum import Enum


class InferenceMode(str, Enum):
    ABDUCTION = "abduction"
    INDUCTION = "induction"
    DEDUCTION = "deduction"
