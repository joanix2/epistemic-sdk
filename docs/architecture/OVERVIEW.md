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

Les contrats sont accompagnés d'algorithmes d'interprétation finie, réécriture bornée, synthèse, validation et sélection d'expériences. La réflexion Maude reste un port non implémenté.

L'expérience ARC ajoute une taxonomie interne de langages M2 : un graphe de versions immuables, des spécialisations par tâche, des opérateurs typés sur grilles/objets et des définitions apprises réutilisables. Les réponses de test ne participent pas à la sélection des programmes. Voir ADR-007, `TECHNICAL.md` et `docs/experiments/arc-taxonomy/REPORT.md`. Cette expérience ne valide pas encore la boucle complète de révision des connaissances ni une découverte autonome de la taxonomie.

## Invariants

Voir `AGENTS.md` (10 invariants). Rappel essentiel : une hypothèse est un programme déclaratif ; une observation n'est pas nécessairement vraie ; une croyance n'est pas une connaissance ; un axiome n'est pas une hypothèse corroborée ; une connaissance reste révisable ; transformation de programme ≠ transformation de résultat ; validation sur observations indépendantes ; provenance préservée.

## Cartographie détaillée

Voir `docs/architecture/DEPENDENCIES.md` (graphe de dépendances) et `AGENTS.md` (carte des modules par agent).
