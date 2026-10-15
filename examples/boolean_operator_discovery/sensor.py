"""Simulated sensor over the black-box boolean operator.

The sensor plays the role of the environment: it *knows* the deterministic,
noise-free truth table of the black box (here XOR) and reports a limited number
of observations. The inference engine only ever sees the observations this
sensor emits — never the table itself.
"""

from datetime import datetime, timezone

from epistemic_sdk import Observation

from .boolean_language import BooleanSample

_TRAINING_CASES = (
    (False, False, False),
    (False, True, True),
    (True, True, False),
)
_VALIDATION_CASE = (True, False, True)


class BooleanSensor:
    """A fixed deterministic sensor: 3 training observations + 1 held-out case.

    The held-out case is deliberately kept in a separate method so it can never
    be passed to the inference engine together with the training data.
    """

    def __init__(self, sensor_id: str = "blackbox") -> None:
        self._sensor_id = sensor_id

    def observe(self) -> tuple[Observation[BooleanSample], ...]:
        """Return the three training observations (obs_1, obs_2, obs_3)."""
        observations: list[Observation[BooleanSample]] = []
        for index, (a, b, output) in enumerate(_TRAINING_CASES, start=1):
            observations.append(
                Observation(
                    id=f"obs_{index}",
                    sensor_id=self._sensor_id,
                    value=BooleanSample(a=a, b=b, output=output),
                    timestamp=datetime.now(timezone.utc),
                    metadata={"source": "training"},
                )
            )
        return tuple(observations)

    def validation_observation(self) -> Observation[BooleanSample]:
        """Return the held-out observation (True, False) -> True."""
        a, b, output = _VALIDATION_CASE
        return Observation(
            id="obs_test",
            sensor_id=self._sensor_id,
            value=BooleanSample(a=a, b=b, output=output),
            timestamp=datetime.now(timezone.utc),
            metadata={"source": "validation"},
        )
