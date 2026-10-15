# Epistemic SDK — interfaces épistémologiques typées

SDK épistémique exécutable, inspiré de Maude, en Python 3.10+. Il fournit les **interfaces** d'une boucle épistémologique : construire, exécuter, corroborer, réfuter et réviser des connaissances, en distinguant strictement **hypothèse**, **croyance** et **connaissance**.

## Statut

Le dépôt livre **les interfaces uniquement** : des `typing.Protocol` pour les ports remplaçables et des `dataclass(frozen=True)` pour les objets de valeur. **Aucun moteur n'est encore implémenté** — pas d'interpréteur Maude, de synthèse, d'exécuteur ni de solveur. Bibliothèque standard uniquement, aucune dépendance tierce.

## Niveaux M3 → M0

| Niveau | Contenu | Module |
|---|---|---|
| **M3** | Métamodèle algébrique général : sortes, opérateurs, termes, équations, axiomes, règles de réécriture, réflexion (`ReflectiveM3`) | `epistemic_sdk/m3/` |
| **M2** | Langage déclaratif instancié depuis M3, versionné (`LanguageM2`) | `epistemic_sdk/m2/` |
| **M1** | Programme déclaratif = hypothèse (`ProgramM1` dans un `LanguageM2`) | `epistemic_sdk/m1/` |
| **M0** | Observations, valeurs, résultats d'exécution | `observations/`, `execution/` |

## Boucle épistémologique

```
Sensor → Observation → BeliefGraph → InferenceEngine → Hypothesis
  → ProgramTransformation → Executor → ResultTransformation → ExecutionResult
  → Validator → KnowledgeReviser → KnowledgeBase → itération
```

Diagramme détaillé (boucle + pile M3→M0) : voir [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md).

## Modules

| Module | Responsabilité |
|---|---|
| `epistemic_sdk/m3/` | Sort, Opérateur, Terme, Équation, Axiome, Règle de réécriture, réflexion (`ReflectiveM3`) |
| `epistemic_sdk/m2/` | `LanguageM2` versionné (sortes, opérateurs, axiomes, subsorts) |
| `epistemic_sdk/m1/` | `ProgramM1`, `Hypothesis`, `InferenceMode` |
| `epistemic_sdk/observations/` | `Observation` (provenance), `Sensor` |
| `epistemic_sdk/beliefs/` | `Belief`, `BeliefGraph`, `Relation`, `BeliefUpdater` |
| `epistemic_sdk/inference/` | `InferenceEngine` (abduction/induction/déduction) |
| `epistemic_sdk/execution/` | `ProgramTransformation`, `ResultTransformation`, `TransformationPipeline` + `Executor`, `ProgramRunner`, `ExecutionContext`, `ExecutionResult` |
| `epistemic_sdk/validation/` | `Validator`, `ValidationReport`, `ValidationStatus` |
| `epistemic_sdk/knowledge/` | `Knowledge`, `KnowledgeBase`, `KnowledgeReviser`, `KnowledgeStatus` |
| `epistemic_sdk/engine/` | `EpistemicEngine` (orchestration d'un cycle) |

## Installation et commandes

L'installation est facultative (`pip install -e .`). Le projet utilise `uv` pour le développement.

```bash
uv sync                                            # install (editable) + outils de dev
uv run python -m unittest discover -s tests -v     # tests de contrats
uv run python -m examples.nat_language             # exemple M2/M1
uv run python scripts/harness.py check             # vérifications légères (imports, invariants)
uv run python scripts/harness.py run               # exécution du harness (tests, avec cache)
uv run python scripts/harness.py run --no-cache    # force l'exécution sans cache
```

Outillage de développement :

```bash
uv run ruff check .                                # lint
uv run mypy epistemic_sdk                          # typage statique
uv run graphify extract . --code-only              # graphe de code (optionnel)
```

## API publique

`epistemic_sdk` expose **40 symboles** (contrat public, documenté par `__all__`) : sortes, opérateurs, termes et lois M3 ; `LanguageM2` ; `ProgramM1`, `Hypothesis`, `InferenceMode` ; `Observation`, `Sensor` ; croyances ; inférence ; exécution ; validation ; connaissance ; `EpistemicEngine`. Toute modification de signature est une **décision architecturale** — voir [`docs/architecture/DECISIONS.md`](docs/architecture/DECISIONS.md).

## Exemple

```python
from epistemic_sdk import (
    Application, Axiom, Equation, Hypothesis, InferenceMode,
    LanguageM2, Operator, ProgramM1, RewriteRule, Sort, Variable,
)

X = Variable("X", "Nat")
Y = Variable("Y", "Nat")
ZERO = Application("zero", ())

def succ(t):
    return Application("succ", (t,))

def add(a, b):
    return Application("add", (a, b))

nat = LanguageM2(
    id="nat", version="1.0.0", sorts=(Sort("Nat"),),
    operators=(
        Operator("zero", (), "Nat"),
        Operator("succ", ("Nat",), "Nat"),
        Operator("add", ("Nat", "Nat"), "Nat"),
    ),
    axioms=(
        Axiom("add_zero_left", Equation(add(ZERO, Y), Y), "definition"),
        Axiom("add_successor", Equation(add(succ(X), Y), succ(add(X, Y))), "definition"),
    ),
)

hypothesis = Hypothesis(
    id="H1",
    program=ProgramM1(
        language_id="nat", language_version="1.0.0",
        entrypoint=add(succ(ZERO), ZERO),
        candidate_rules=(RewriteRule(add(X, ZERO), X),),
    ),
    inference_mode=InferenceMode.INDUCTION,
)
```

Voir [`examples/nat_language.py`](examples/nat_language.py) — cet exemple déclare une **théorie**, pas un runtime Maude.

## Invariants architecturaux

1. Une hypothèse est un programme déclaratif (`ProgramM1`), pas une proposition textuelle.
2. Un programme est défini relativement à un langage M2 (identifiant + version).
3. M3 est un métamodèle général, avec des propriétés réflexives à implémenter et vérifier.
4. Une observation n'est pas nécessairement vraie.
5. Une croyance n'est pas une connaissance.
6. Un axiome admis dans une théorie n'est pas une hypothèse corroborée empiriquement.
7. Une connaissance reste révisable en présence de nouveaux contre-exemples.
8. Transformation de programme et transformation de résultat sont deux étapes distinctes.
9. La validation porte sur des résultats d'exécution confrontés à des observations **indépendantes** (aucune fuite entraînement/test).
10. Toute connaissance préserve la provenance de ses hypothèses, exécutions et validations.

## Documentation

- [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) — diagrammes Mermaid (boucle + pile M3→M0).
- [`docs/architecture/OVERVIEW.md`](docs/architecture/OVERVIEW.md) — vue d'ensemble.
- [`docs/architecture/DECISIONS.md`](docs/architecture/DECISIONS.md) — journal des décisions (ADR).
- [`docs/architecture/DEPENDENCIES.md`](docs/architecture/DEPENDENCIES.md) — graphe de dépendances entre modules.
- [`AGENTS.md`](AGENTS.md) — contexte partagé des agents (carte des modules, conventions, protocole de délégation).
