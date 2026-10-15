# Vue d'ensemble de l'architecture

Epistemic SDK implémente une boucle épistémologique : construire, exécuter, corroborer, réfuter et réviser des connaissances, en distinguant strictement **hypothèse**, **croyance** et **connaissance**.

## Boucle

```
Sensor → Observation → BeliefGraph → InferenceEngine → Hypothesis
  → ProgramTransformation → Executor → ResultTransformation → ExecutionResult
  → Validator → KnowledgeReviser → KnowledgeBase → itération
```

## Niveaux M3 → M0

| Niveau | Contenu | Module |
|---|---|---|
| M3 | Métamodèle algébrique général : sortes, opérateurs, termes, équations, axiomes, règles de réécriture, réflexion Maude | `epistemic_sdk/m3/` |
| M2 | Langage déclaratif instancié depuis M3, versionné | `epistemic_sdk/m2/` |
| M1 | Programme déclaratif = hypothèse, dans un `LanguageM2` | `epistemic_sdk/m1/` |
| M0 | Observations, valeurs, résultats d'exécution | `observations/`, `execution/` |

## Composants

- **Observations** : `Observation` (provenance, horodatage, métadonnées), `Sensor`.
- **Croyances** : `Belief`, `BeliefGraph`, `Relation`, `BeliefUpdater`.
- **Inférence** : `InferenceEngine` (abduction/induction/déduction) → `Hypothesis` (`ProgramM1`).
- **Exécution** : `ProgramTransformation` → `Executor` → `ResultTransformation` → `ExecutionResult`.
- **Validation** : `Validator` → `ValidationReport` (`corroborated`/`refuted`/`inconclusive`).
- **Connaissance** : `Knowledge`, `KnowledgeBase`, `KnowledgeReviser`.
- **Moteur** : `EpistemicEngine` (orchestration d'un cycle).

## État réel

- Le dépôt contient **les interfaces** (`dataclass(frozen=True)` + `typing.Protocol`), un exemple M2 (`examples/nat_language.py`) et des tests de contrats (`tests/test_contracts.py`).
- **Aucun moteur n'est implémenté** : pas d'interpréteur Maude, de synthèse, d'exécuteur ni de solveur. Les `Protocol` sont des ports remplaçables, pas des implémentations.

## Invariants

Voir `AGENTS.md` (10 invariants). Rappel essentiel : une hypothèse est un programme déclaratif ; une observation n'est pas nécessairement vraie ; une croyance n'est pas une connaissance ; un axiome n'est pas une hypothèse corroborée ; une connaissance reste révisable ; transformation de programme ≠ transformation de résultat ; validation sur observations indépendantes ; provenance préservée.

## Cartographie détaillée

Voir `docs/architecture/DEPENDENCIES.md` (graphe de dépendances) et `AGENTS.md` (carte des modules par agent).
