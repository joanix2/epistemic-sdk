<!-- BEGIN AGENT KANBAN — DO NOT EDIT THIS SECTION -->
## Agent Kanban

Read `.agentkanban/INSTRUCTION.md` for task workflow rules.
Read `.agentkanban/memory.md` for project context.

If a task file (`.agentkanban/tasks/**/*.md`) was referenced earlier in this conversation, re-read it before responding and always respond in and at the end the task file.
<!-- END AGENT KANBAN -->

# Epistemic SDK — Contexte partagé des agents

Projet : SDK épistémique exécutable, inspiré de Maude, en Python 3.10+. Le dépôt contient les interfaces publiques, des algorithmes concrets dans `epistemic_sdk/algorithms/`, les expériences booléennes et ARC, et leurs tests. Un interpréteur fini et de la synthèse bornée existent ; aucun moteur réflexif Maude n'est implémenté. État mesuré : `PROGRESS.md` et `docs/experiments/arc-taxonomy/REPORT.md`.

## Objectif scientifique

Implémenter une boucle épistémologique : construire, exécuter, corroborer, réfuter et réviser des connaissances, en distinguant strictement hypothèse, croyance et connaissance.

Boucle : `Sensor → Observation → BeliefGraph → InferenceEngine → Hypothesis → ProgramTransformation → Executor → ResultTransformation → ExecutionResult → Validator → KnowledgeReviser → KnowledgeBase → itération`.

Quatre niveaux :
- **M3** : algèbre de termes typés, métamodèle réflexif (Maude), équations, axiomes, règles de réécriture.
- **M2** : langages déclaratifs instanciés depuis M3 (`LanguageM2` versionné).
- **M1** : programmes déclaratifs = hypothèses (`ProgramM1` dans un `LanguageM2`).
- **M0** : observations, valeurs, résultats d'exécution.

## Objectif principal de l'expérience de validation

L'expérience de validation d'Epistemic SDK cherche à répondre à **trois problèmes fondamentaux** :

1. **Découverte (inférence)** — comment générer une hypothèse, sous forme de programme déclaratif, à partir d'un ensemble limité d'observations, sans connaître la solution à l'avance ?
2. **Composition (architecture)** — comment faire fonctionner ensemble les composants du SDK (observations, croyances, inférence, transformations, exécution, validation) sans créer de dépendances artificielles ?
3. **Réfutation (révision des connaissances)** — comment utiliser de nouvelles observations pour identifier des contre-exemples, réfuter les hypothèses incompatibles et réviser les connaissances déjà acquises ?
4. **Définition du sous-espace de recherche (définition automatique du M2)** — comment définir automatiquement le sous-espace de recherche (le langage M2) dans lequel l'inférence opère, plutôt que de le fixer manuellement ?

### Problème plus profond : l'émergence

Le bon programme peut être isolé dans un espace de recherche immense, **sans gradient** permettant de s'en approcher progressivement. C'est précisément pourquoi on a décidé de **fixer M2** et de commencer avec un espace de programmes limité, avant de permettre au système de faire évoluer ses propres langages.

L'expérience booléenne (`examples/boolean_operator_discovery/`) teste surtout la **découverte**, la **composition** et la **réfutation**. Elle **ne résout pas encore** le problème général de la recherche dans un espace de programmes arbitraires.

## Boucle épistémique active

Au-delà de la boucle passive (les observations sont données), le SDK vise une boucle **active** : la connaissance reconfigure la politique expérimentale.

- Deux distributions couplées : `P(H | D)` sur les hypothèses et `P(E | D)` sur les expériences à mener.
- Un contre-exemple ne fait pas que baisser `P(H)` : il **réoriente** `P(E)` — où chercher ensuite.
- Sélection d'expérience : `e* = argmax_e E[I(H ; Y_e)]` (information mutuelle attendue) ; sur domaine fini, un proxy de désaccord suffit.
- Contrôleur supérieur `{tester, explorer, abduire}` : si toutes les hypothèses échouent, `P(abduire)` monte — élargir l'espace `H` (problème #4).
- `Belief.confidence` est la graine de `P(H)` ; le port `ExperimentSelector` est le mécanisme de `P(E)`.

## Carte des modules

| Module | Responsabilité | Agent |
|---|---|---|
| `epistemic_sdk/m3/` | Sort, Opérateur, Terme, Équation, Axiome, Règle de réécriture, réflexion (`ReflectiveM3`) | m3-algebra |
| `epistemic_sdk/m2/` | `LanguageM2` versionné (sortes, opérateurs, axiomes, subsorts) | m2-language |
| `epistemic_sdk/m1/` | `ProgramM1`, `Hypothesis`, `InferenceMode` | inference |
| `epistemic_sdk/observations/` | `Observation` (provenance), `Sensor` | observations |
| `epistemic_sdk/beliefs/` | `Belief`, `BeliefGraph`, `Relation`, `BeliefUpdater` | beliefs |
| `epistemic_sdk/inference/` | `InferenceEngine` (abduction/induction/déduction), `ExperimentSelector` (boucle active) | inference |
| `epistemic_sdk/execution/` | `ProgramTransformation`, `ResultTransformation`, `TransformationPipeline` | transformations |
| `epistemic_sdk/execution/` | `Executor`, `ProgramRunner`, `ExecutionContext`, `ExecutionResult` | execution |
| `epistemic_sdk/validation/` | `Validator`, `ValidationReport`, `ValidationStatus` | validation |
| `epistemic_sdk/knowledge/` | `Knowledge`, `KnowledgeBase`, `KnowledgeReviser`, `KnowledgeStatus` | knowledge |
| `epistemic_sdk/engine/` | `EpistemicEngine` (orchestration d'un cycle) | epistemic-engine |
| `tests/`, `scripts/` | tests multi-niveaux, harness | test-harness |

`transformations` et `execution` partagent `epistemic_sdk/execution/` : le premier possède les fichiers `*_transformation*.py` et `transformation_pipeline.py`, le second possède `executor.py` et `program_runner.py`. Toute modification croisée dans ce répertoire doit être coordonnée par l'architecte.

## Invariants architecturaux

1. Une hypothèse est un programme déclaratif, pas une proposition textuelle.
2. Un programme est défini relativement à un langage M2 (identifiant + version).
3. M3 est un métamodèle général, avec des propriétés réflexives à implémenter et vérifier.
4. Une observation n'est pas nécessairement vraie.
5. Une croyance n'est pas une connaissance.
6. Un axiome admis dans une théorie n'est pas une hypothèse corroborée empiriquement.
7. Une connaissance reste révisable en présence de nouveaux contre-exemples.
8. Transformation de programme et transformation de résultat sont deux étapes distinctes.
9. La validation porte sur des résultats d'exécution confrontés à des observations **indépendantes** (aucune fuite entraînement/test).
10. Toute connaissance préserve la provenance de ses hypothèses, exécutions et validations.
11. Une connaissance n'est pas seulement une croyance ; elle détermine quelles observations valent la peine d'être recherchées.

## Conventions Python et typage

- Python 3.10+ (syntaxe `X | Y`), `dataclass(frozen=True)` pour les objets de valeur.
- Bibliothèque standard uniquement pour les interfaces ; une dépendance tierce ne s'ajoute à `pyproject.toml` que sur justification validée par l'architecte.
- Typer les APIs publiques : `typing.Protocol` pour les ports remplaçables, `TypeVar`/`Generic` pour les conteneurs.
- Documenter les limites et les non-preuves dans les docstrings ; pas de commentaires superflus.
- Ne jamais revendiquer une propriété formelle (terminaison, confluence, normalisation) non démontrée ni testée.

## Politique de modification des interfaces publiques

- Les `dataclass`/`Protocol` publiés dans `epistemic_sdk/__init__.py` sont un contrat public.
- Toute modification de signature est une **décision architecturale** : la documenter dans `docs/architecture/DECISIONS.md`, mettre à jour les tests de contrats, et la faire valider par l'architecte.
- Ajouter est autorisé ; renommer/supprimer/retyper un champ public exige justification et migration.
- Changer la définition d'un `LanguageM2` exige un changement de sa `version`.

## Commandes

```bash
python -m unittest discover -s tests -v      # tests de contrats
python -m examples.nat_language               # exemple M2/M1
python scripts/harness.py check               # vérifications légères (imports, invariants)
python scripts/harness.py run                 # exécution du harness (tests)
python scripts/harness.py run --no-cache      # force l'exécution sans cache
```

`ruff` et `mypy` sont configurés dans `pyproject.toml`. Vérifications : `.venv/bin/ruff check .` et `.venv/bin/mypy epistemic_sdk examples tests`. Ne pas ajouter d'autre outil sans nécessité explicite.

## Protocole de délégation

Voir `docs/harness/PROTOCOL.md`. Résumé : l'architecte découpe en tâches, émet un **contrat** (Task ID, objectif, périmètre de fichiers, interfaces, invariants, critères d'acceptation, tests, dépendances, budget), délègue à un sous-agent spécialisé, récupère un **rapport structuré** (modifications, interfaces, tests, propriétés vérifiées, incertitudes, risques, décisions). Ne pas déléguer une tâche triviale. Pas d'écritures concurrentes sur un même fichier. Parallélisme initial limité à 3.

## Cache et invalidation

Voir `docs/harness/CACHE.md`. Trois couches : (A) contexte LLM — instructions stables, chargement progressif, compaction native d'OpenCode ; (B) développement — relancer les tests si une dépendance est incertaine, contournement via `--no-cache` ; (C) sémantique épistémologique — **à concevoir**, pas encore implémentée. Une nouvelle observation ou un axiome modifié invalide les résultats dépendants. Ne jamais réutiliser une corroboration sur la seule identité d'une hypothèse.

## Gestion du contexte

Charger les documents à la demande (`docs/architecture/*.md`, `docs/harness/*.md`) ; ne jamais lire tout le dépôt pour une modification locale. `docs/harness/STATE.md` est la mémoire de reprise (en cours, résultats confirmés, prochains objectifs, blocages) — pas un second historique Git.

## Définition de Done

Une tâche est terminée si : modifications réalisées ; interfaces cohérentes ; tests appropriés passent ; erreurs et limites documentées ; provenance préservée ; aucun module non concerné modifié sans justification ; l'architecte a intégré et vérifié. Une tâche en échec n'est jamais marquée terminée.
