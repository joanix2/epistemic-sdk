# Expérience 001 — Découverte d'un opérateur booléen

Première instance expérimentale complète du framework : découvrir un opérateur
booléen inconnu (XOR) à partir de **trois observations**, en utilisant **toute**
la boucle épistémologique du SDK — sans LLM, sans coder la réponse en dur.

## L'exercice

Une boîte noire déterministe calcule `f: Bool × Bool → Bool`. Un capteur fournit
trois observations d'entraînement et conserve une quatrième pour la validation
indépendante :

| ID | A | B | Résultat |
|---|---|---|---|
| `obs_1` | F | F | F |
| `obs_2` | F | T | T |
| `obs_3` | T | T | F |
| `obs_test` (validation) | T | F | T |

Le moteur doit retrouver `XOR` parmi `{AND, OR, XOR, NAND, NOR, XNOR}`.

## Lancer

```bash
python -m examples.boolean_operator_discovery
```

## Boucle implémentée

```
Sensor → Observation → BeliefUpdater → BeliefGraph → InferenceEngine (6 candidats)
→ ProgramTransformation (not(not(X)) → X) → ProgramRunner/Executor → ExecutionResult
→ Validator (ajustement puis validation indépendante) → KnowledgeReviser → KnowledgeBase
```

## Fichiers

| Fichier | Responsabilité |
|---|---|
| `boolean_language.py` | Langage M2 booléen (sortes, opérateurs, axiomes de table de vérité, `not(not(X))=X`) |
| `sensor.py` | Capteur simulé (3 observations + 1 de validation) |
| `belief_updater.py` | Observations → croyances `f(a, b) = output` |
| `inference.py` | Génération des 6 candidats + élimination par exécution |
| `transformation.py` | `NotNotElimination` (normalise `not(not(op(A,B)))` en `op(A,B)`) |
| `interpreter.py` | Interpréteur booléen (réutilise `FiniteInterpreter` de la Phase 1) |
| `validator.py` | `BooleanValidator` (ajustement vs validation indépendante) |
| `knowledge_reviser.py` | Enregistre le programme corroboré comme connaissance active |
| `engine.py` | Orchestration (`BooleanDiscoveryEngine`) |

## Résultat attendu

- Programme découvert : `XOR(A, B)`.
- Prédiction sur `(True, False)` : `True` — corroboré.
- Une connaissance active est enregistrée avec sa provenance (hypothèse, exécution, rapport de validation).

Les tests correspondants sont dans `tests/test_boolean_discovery.py`.
