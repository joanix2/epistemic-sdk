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

L'expérience de validation d'Epistemic SDK cherche à répondre à **quatre problèmes fondamentaux** :

1. **Découverte (inférence)** — comment générer une hypothèse, sous forme de programme déclaratif, à partir d'un ensemble limité d'observations, sans connaître la solution à l'avance ?
2. **Composition (architecture)** — comment faire fonctionner ensemble les composants du SDK (observations, croyances, inférence, transformations, exécution, validation) sans créer de dépendances artificielles ?
3. **Réfutation (révision des connaissances)** — comment utiliser de nouvelles observations pour identifier des contre-exemples, réfuter les hypothèses incompatibles et réviser les connaissances déjà acquises ?
4. **Définition du sous-espace de recherche (définition automatique du M2)** — comment définir automatiquement le sous-espace de recherche (le langage M2) dans lequel l'inférence opère, plutôt que de le fixer manuellement ?

### Recherche et création de langage (problème #4 en détail)

Le langage M2 est lui-même une hypothèse : il détermine quels programmes M1 peuvent être exprimés, donc quelles hypothèses existent. Choisir M2 revient à choisir le sous-espace où chercher. Les objectifs, du plus simple au plus ambitieux :

1. **Sélection** — parmi des familles de langages données (taxonomie de M2), choisir celle(s) à explorer pour une tâche, à partir des seules observations d'entraînement. *État : heuristique manuelle d'ordre de familles (`TaxonomicSolver`) ; aucune sélection apprise.*
2. **Spécialisation** — dériver un M2 de tâche à partir de versions immuables de familles partagées (héritage, versions, provenance), y compris des opérateurs dont les paramètres sont estimés sur les observations (apprenants ajustés, ADR-008). *État : implémenté ; les descripteurs et familles de départ sont écrits à la main.*
3. **Enrichissement** — promouvoir une composition corroborée en nouvel opérateur d'une famille (abstraction), avec statut `candidate`, provenance et versionnement. Le transfert entre tâches doit être mesuré en coût de recherche, pas seulement en nombre de réutilisations. *État : implémenté, gain de transfert non établi.*
4. **Invention** — créer des sortes, opérateurs, axiomes ou familles absents du langage de départ, quand toutes les hypothèses d'un M2 échouent (montée de `P(abduire)`), puis les valider sur des observations indépendantes. *État : non résolu ; les primitives sont fournies par l'humain.*
5. **Découverte de taxonomie** — organiser automatiquement les familles et les relations de transfert (conditions d'applicabilité, traductions entre représentations). *État : non résolu.*

Exigences pour toute étape de recherche ou de création de langage :

- Chaque langage créé ou modifié est versionné et porte sa provenance (observations, hypothèses, validations qui l'ont motivé).
- Un langage est jugé sur des observations indépendantes de celles qui l'ont produit ; l'ajustement exact à l'entraînement est un indice, pas une preuve.
- Un langage plus expressif élargit l'espace sans gradient : mesurer le coût (candidats, nœuds) autant que la couverture, et rapporter l'écart entre développement et évaluation.
- Séparer strictement les niveaux : primitives (M0/M1) → descripteurs et apprenants → familles M2 → politique de choix de famille → révision des connaissances. Un module ne dépend que des niveaux inférieurs.
- Les langages et leurs résultats restent révisables : un contre-exemple doit pouvoir invalider une abstraction promue et les résultats qui en dépendent.

### Problème plus profond : l'émergence

Le bon programme peut être isolé dans un espace de recherche immense, **sans gradient** permettant de s'en approcher progressivement. C'est précisément pourquoi on a décidé de **fixer M2** et de commencer avec un espace de programmes limité, avant de permettre au système de faire évoluer ses propres langages.

L'expérience booléenne (`examples/boolean_operator_discovery/`) teste surtout la **découverte**, la **composition** et la **réfutation**. Elle **ne résout pas encore** le problème général de la recherche dans un espace de programmes arbitraires.

## Règle critique : pas de fonction complexe écrite en dur

Un score qui monte grâce à une fonction complexe écrite à la main donne l'impression de réussir, mais c'est de la **dette technique** : la connaissance est dans le code de l'humain, pas découverte par le système. Cette règle prime sur tout objectif de score.

**Autorisé (primitives de base, petites, typées, réutilisables)** : logique booléenne (`and`, `or`, `xor`, `not`), transformations spatiales (flip, rotation, transposition, décalage, scale, découpe, concaténation), changement de couleur, morphologie (composantes, trous, dilatation). Estimer une **constante** (couleur, entier, table de recoloration) sur les observations est aussi autorisé.

**Interdit** :
- Écrire en dur une fonction complexe (tuilage, partition/combinaison, fractale, extraction, règle locale, etc.) qui encode la structure d'une solution, y compris sous forme d'« apprenant », de « famille ajustée » ou d'opérateur `task_*`.
- Ajouter une primitive dont le nom ou le comportement correspond à une tâche, à une famille de tâches ou à une solution observée dans les données.
- Régler une heuristique en lisant les échecs d'un jeu de tâches puis rapporter le score obtenu sur ce même jeu comme une capacité du système.

**Obligatoire** :
- Une fonction complexe est une **composition de primitives retrouvée par recherche**, puis **stockée** par le système (promotion en opérateur `candidate`, version, provenance, validation indépendante).
- Tout programme retenu doit rester un terme M1 lisible : on doit pouvoir y lire les étapes (séparer, intersecter, recolorer…), pas un opérateur opaque ou une fermeture.
- Avant d'ajouter du code qui améliore un score, se demander : « est-ce une primitive, ou la solution déguisée ? » En cas de doute, ne pas l'ajouter et en discuter avec l'utilisateur.
- Tout score est rapporté avec sa décomposition : tâches résolues par primitives composées, par apprenant/opérateur écrit en dur, et par abstraction promue. Seuls les deux dernières lignes ne comptent pas comme découverte.
- Un code existant qui viole cette règle est de la dette : le marquer comme tel (docstring, `PROGRESS.md`), le mesurer en ablation, et le supprimer quand la recherche retrouve les mêmes tâches. Ne jamais l'étendre.

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
12. Les fonctions complexes sont retrouvées et stockées par le système, jamais écrites en dur (voir « Règle critique »).

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
