"""Experiment 001 — Boolean operator discovery.

Run: ``python -m examples.boolean_operator_discovery``

Discovers the black-box operator (XOR) from three training observations using
the full epistemic loop, then validates the prediction on a held-out case.
"""

import json

from epistemic_sdk.execution.program_runner import ProgramRunner

from .belief_updater import BooleanBeliefUpdater
from .boolean_language import BOOLEAN_LANGUAGE, BooleanSample
from .engine import BooleanDiscoveryEngine, DiscoveryResult
from .inference import BooleanInferenceEngine
from .interpreter import BOOLEAN_INTERPRETER
from .knowledge_reviser import BooleanKnowledgeReviser
from .sensor import BooleanSensor
from .transformation import NotNotElimination
from .validator import BooleanValidator


def _build_engine() -> BooleanDiscoveryEngine:
    transformation = NotNotElimination()
    runner = ProgramRunner(executor=BOOLEAN_INTERPRETER, transformations=(transformation,))
    inference = BooleanInferenceEngine(runner)
    return BooleanDiscoveryEngine(
        belief_updater=BooleanBeliefUpdater(),
        inference=inference,
        runner=runner,
        validator=BooleanValidator(),
        reviser=BooleanKnowledgeReviser(),
    )


def _summary(result: DiscoveryResult) -> dict:
    return {
        "language": {"id": result.language_id, "version": result.language_version},
        "training": [
            {"id": o.id, "a": o.value.a, "b": o.value.b, "output": o.value.output}
            for o in result.training_observations
        ],
        "validation": {
            "id": result.test_observation.id,
            "a": result.test_observation.value.a,
            "b": result.test_observation.value.b,
            "output": result.test_observation.value.output,
        },
        "candidates": list(result.candidate_operators),
        "refuted": [
            {
                "hypothesis": r.hypothesis.id,
                "counterexample": {"a": r.counterexample.a, "b": r.counterexample.b},
            }
            for r in result.trace.refutations
        ],
        "selected": result.selected.id if result.selected else None,
        "prediction": result.prediction,
        "validation_status": result.report.status.value if result.report else None,
        "knowledge": [
            {"id": k.id, "hypothesis_id": k.hypothesis_id, "status": k.status.value}
            for k in result.knowledge.entries
        ],
    }


def _render(sample: BooleanSample) -> str:
    return f"({sample.a}, {sample.b}) -> {sample.output}"


def main() -> None:
    sensor = BooleanSensor()
    training = sensor.observe()
    test = sensor.validation_observation()
    result = _build_engine().run(training, test)

    print("=" * 62)
    print("Expérience 001 — Découverte d'un opérateur booléen")
    print("=" * 62)
    print("1. Langage M2 chargé")
    print(f"   {result.language_id} v{result.language_version} "
          f"({len(BOOLEAN_LANGUAGE.operators)} opérateurs, "
          f"{len(BOOLEAN_LANGUAGE.axioms)} axiomes)")
    print("2. Observations collectées (entraînement)")
    for obs in result.training_observations:
        print(f"   {obs.id}: {_render(obs.value)}")
    print(f"   {result.test_observation.id} (validation): {_render(test.value)}")
    print("3. Croyances et relations")
    for belief in result.beliefs.beliefs:
        print(f"   {belief.id}: {_render(belief.proposition)} "
              f"(soutenue par {belief.evidence_ids})")
    print("4. Hypothèses candidates")
    print(f"   {', '.join(result.candidate_operators)}")
    print("5. Transformation de programmes (not(not(X)) -> X)")
    print("   nom de transformation : not_not_elimination")
    print("6. Sorties exécutées et 7. réfutations")
    for refutation in result.trace.refutations:
        print(f"   {refutation.hypothesis.id} RÉFUTÉE — contre-exemple "
              f"{_render(refutation.counterexample)}")
    for hypothesis in result.trace.surviving:
        print(f"   {hypothesis.id} survit (compatible avec les 3 observations)")
    print("8. Hypothèse sélectionnée")
    print(f"   {result.selected.id if result.selected else 'aucune'}")
    print("9. Prédiction sur l'exemple indépendant")
    print(f"   {_render(test.value)}  ->  prédiction: {result.prediction}")
    if result.report is not None:
        print(f"   statut: {result.report.status.value}")
    print("10. Connaissance enregistrée")
    for knowledge in result.knowledge.entries:
        print(f"   {knowledge.id}: {knowledge.status.value} "
              f"(hypothèse {knowledge.hypothesis_id})")

    print("-" * 62)
    print("Résumé JSON :")
    print(json.dumps(_summary(result), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
