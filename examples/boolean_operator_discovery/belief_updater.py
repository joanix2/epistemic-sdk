"""Turn raw observations into interpreted beliefs of the form f(A, B) = output.

A raw observation is not a belief: the belief is the interpreted statement
"the black box maps (a, b) to ``output``", supported by the observation that
recorded it. This module keeps that distinction explicit.
"""

from epistemic_sdk import Belief, BeliefGraph, Observation, Relation, RelationType

from .boolean_language import BooleanSample


class BooleanBeliefUpdater:
    """Assimilate boolean observations into a ``BeliefGraph[BooleanSample]``."""

    def update(
        self,
        graph: BeliefGraph[BooleanSample],
        observations: tuple[Observation[BooleanSample], ...] | list[Observation[BooleanSample]],
    ) -> BeliefGraph[BooleanSample]:
        new_beliefs = list(graph.beliefs)
        new_relations = list(graph.relations)
        for observation in observations:
            sample = observation.value
            if not isinstance(sample, BooleanSample):
                raise TypeError(f"expected a BooleanSample, got {type(sample).__name__}")
            belief_id = f"belief_{int(sample.a)}_{int(sample.b)}"
            if all(belief.id != belief_id for belief in new_beliefs):
                new_beliefs.append(
                    Belief(
                        id=belief_id,
                        proposition=sample,
                        confidence=1.0,
                        evidence_ids=(observation.id,),
                    )
                )
            new_relations.append(
                Relation(
                    source_id=observation.id,
                    target_id=belief_id,
                    type=RelationType.SUPPORTS,
                )
            )
        return BeliefGraph(
            observations=graph.observations + tuple(observations),
            beliefs=tuple(new_beliefs),
            relations=tuple(new_relations),
            version=graph.version + 1,
        )
