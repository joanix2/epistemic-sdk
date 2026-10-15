---
title: Implémenter les instances d'algorithmes (génétiques, EBM, ILP, MLP, Z3)
lane: todo
created: 2026-10-15T11:22:52
updated: 2026-10-15T11:22:52
description: Implémenter des synthétiseurs/solveurs concrets : algorithmes génétiques, EBM, ILP, MLP et Z3 derrière les interfaces.
---

## Conversation

### user

Implémenter les différentes instances avec plusieurs algorithmes : génétiques, EBM, ILP, MLP et Z3.

### agent

Ticket créé. Objectif : fournir des implémentations concrètes des interfaces — algorithme génétique, EBM (programmation évolutionnaire), ILP (programmation logique inductive), MLP (réseau de neurones) et solveur Z3 — chacune derrière la même interface de synthèse.

### user

Ajoute à l'historique du ticket un tableau d'algorithmes connus et leur type. Ex. : les ILP aident à l'inférence (partie abductive) ; les moteurs SMT comme Z3 servent à la validation de contraintes — ils n'utilisent donc pas les mêmes interfaces du SDK. Z3 peut même servir à construire une factory de Validator.

### agent

Tableau de synthèse : familles d'algorithmes connus, leur type et leur rôle dans la boucle épistémique.

| Algorithme / moteur | Famille (type) | Rôle dans la boucle | Interface SDK cible | Interface native ? |
|---|---|---|---|---|
| ILP — Popper, Metagol, Aleph, Progol | Synthèse inductive / abductive | Inférence : produire des hypothèses (`ProgramM1`) à partir d'observations + connaissances | `InferenceEngine` (abduction/induction) | ✅ Oui — sort un `ProgramM1` |
| Algorithmes génétiques | Recherche heuristique | Inférence : exploration de l'espace des programmes | `InferenceEngine` | ✅ Oui |
| EBM (programmation évolutionnaire) | Recherche évolutionnaire | Inférence : optimisation d'une population de programmes | `InferenceEngine` | ✅ Oui |
| MLP (réseau de neurones) | Apprentissage supervisé (continu) | Assimilation / inférence : fonction apprise, pas un programme symbolique | Adaptateur `InferenceEngine` / `Executor` | ⚠️ Non — sortie non symbolique, traduction requise |
| SMT — Z3, CVC5 | Solveur de contraintes / satisfiabilité | Validation de contraintes, recherche de contre-exemples | `Validator` (factory) | ❌ Non — représentation de termes propre (`z3.Expr`), adaptateur requis |
| Réécriture de termes — Maude, Stratego | Réécriture / normalisation | M3 (runtime réflexif) + `ProgramTransformation` | `ReflectiveM3`, `ProgramTransformation` | ✅ Oui — cœur M3, non implémenté aujourd'hui |

Points clés :

- **ILP → inférence / abduction** : se branche directement sur `InferenceEngine` et produit des `ProgramM1` dans un `LanguageM2`.
- **SMT (Z3) → validation de contraintes** : Z3 manipule sa propre AST (`z3.Expr`), **pas** les `Term` M3 ; il ne peut donc pas s'utiliser tel quel derrière les interfaces, mais sert à construire une **factory de `Validator`** (adaptateur Z3 ↔ `ExecutionResult`/`Observation`).
- Les algorithmes de **synthèse** (ILP, génétique, EBM) partagent le port `InferenceEngine` ; les **solveurs de contraintes** (Z3) relèvent de `Validator` ; les **réécritures** relèvent de M3/`ProgramTransformation`. Chaque famille ne consomme donc pas les mêmes interfaces du SDK.

### user

Peut-être qu'il faut faire un mix : l'ILP propose des règles, l'algorithme génétique engendre des combinaisons plus complexes et l'EBM priorise.

### agent

Bonne piste — plutôt que trois implémentations concurrentes de `InferenceEngine`, on peut les composer en **pipeline de synthèse** à trois étages :

| Étage | Algorithme | Rôle | Sortie SDK |
|---|---|---|---|
| 1. Proposer | ILP (abduction) | Émet des règles candidates | `RewriteRule` → `ProgramM1.candidate_rules` |
| 2. Combiner | Génétique | Compose les règles en programmes/termes plus complexes | `Term` / `Application` → `ProgramM1.entrypoint` |
| 3. Prioriser | EBM | Note et ordonne les hypothèses concurrentes | `Hypothesis` triées (population) |

```
observations + connaissances
   │
   ▼
[ILP — abduire]        → règles candidates (RewriteRule)
   │
   ▼
[Génétique — combiner] → programmes complexes (Term / entrypoint)
   │
   ▼
[EBM — prioriser]      → hypothèses ordonnées (Hypothesis)
   │
   ▼
[Validator / corroboration] → sélection finale (expériences indépendantes)
```

Implications d'architecture :

- **Découplage règle / programme** : `ProgramM1` distingue déjà `candidate_rules` (les règles) et `entrypoint` (le terme composé) — le mix y correspond naturellement.
- **Composition, pas compétition** : un `InferenceEngine` composite peut enchaîner ces trois étages ; chaque étage reste un composant remplaçable (une stratégie injectée).
- **La priorisation EBM n'est pas la décision finale** : elle ordonne les candidats ; la corroboration empirique (`Validator` + observations indépendantes) reste le juge de la boucle.
- **Z3 reste hors de ce pipeline de synthèse** : il intervient en aval (validation de contraintes) ou en amont (filtrage), jamais en production de règles.

### user

Dans tous les cas, je pense qu'il faut se constituer une lib d'algorithmes, qui doivent être contextualisés dans le cadre de notre boucle épistémique ; on pourra piocher en fonction des besoins.

### agent

Oui — c'est la bonne abstraction. Les `Protocol` du SDK sont déjà les **slots** où se branchent les algorithmes ; la « lib d'algo » est donc un **catalogue (registre) d'implémentations**, chacune **contextualisée** par son étage dans la boucle.

**Dimensions de contexte** (métadonnées de chaque entrée du catalogue) :

| Dimension | Valeurs | Rôle |
|---|---|---|
| Port cible | `InferenceEngine`, `Validator`, `ProgramTransformation`, `Executor`, `Sensor`, `BeliefUpdater`, `KnowledgeReviser`, `ReflectiveM3` | quel `Protocol` l'algo satisfait |
| Étage de la boucle | synthèse / validation / réécriture / assimilation / révision | où il intervient dans `Sensor → … → KnowledgeBase` |
| Mode d'inférence | abduction / induction / déduction | pour les `InferenceEngine` |
| Sortie | symbolique (`ProgramM1`) / continu (MLP) / verdict (`ValidationReport`) / observation | type produit |
| Représentation | native (`Term` M3) / propre (adaptateur requis) | s'il consomme les types du SDK |
| Contraintes | domaine fini, bornes, budget, bruit | conditions d'emploi |

**« Piocher selon les besoins » = registre + factory** : un catalogue clé par `(port, capacité)`, d'où l'on tire une implémentation au montage du moteur (esquisse, pas du code livré) :

```
registre.register(InferenceEngine, "ilp",      ILPEngine)
registre.register(InferenceEngine, "genetic",  GeneticEngine)
registre.register(InferenceEngine, "pipeline", ILP → Génétique → EBM)   # le mix discuté
registre.register(Validator,      "z3",        Z3Validator)              # adaptateur
registre.register(ProgramTransformation, "maude", MaudeRewriter)

engine = EpistemicEngine(
    inference=registre.pick(InferenceEngine, "pipeline"),
    validator=registre.pick(Validator, "z3"),
    ...
)
```

**Points d'attention** :

- **Dépendances** : le cœur du SDK reste stdlib ; Z3, MLP (scikit-learn), ILP sont des **adaptateurs optionnels** qui importent leur dépendance à la demande (import paresseux), conformément à la règle « pas de dépendance tierce sans justification ».
- **Le contexte est dans le catalogue, pas dans l'algo** : un même moteur (ex. Z3) peut servir de `Validator` ou de filtre en amont — c'est le registre qui documente l'étage qu'il occupe.
- **La boucle choisit sans connaître les détails** : `EpistemicEngine` ne dépend que des `Protocol`, pas des implémentations concrètes — le registre est le seul point qui connaît l'inventaire.

### user

Pour moi les catégories, c'est des trucs du style abduction, déduction, validation, etc.

### agent

D'accord — la catégorie première est la **fonction épistémique**, pas le port technique. On pioche par « j'ai besoin d'abduction », pas par « j'ai besoin d'un `InferenceEngine` ». Le port n'est qu'un attribut secondaire (l'interface que l'algo satisfait).

**Taxonomie par fonction épistémique** (alignée sur la boucle) :

| Catégorie (fonction) | Ce qu'elle fait | Port(s) associé(s) |
|---|---|---|
| **Abduction** | proposer des règles/hypothèses explicatives | `InferenceEngine` (abduction) |
| **Induction** | généraliser à partir d'exemples | `InferenceEngine` (induction) |
| **Déduction** | dériver des conséquences / vérifier la cohérence | `InferenceEngine` (déduction) |
| **Validation** | confronter à des observations (corroboration / réfutation) | `Validator` |
| **Réécriture** | normaliser / transformer un programme | `ProgramTransformation`, `ReflectiveM3` |
| **Exécution** | évaluer un programme dans un contexte | `Executor` |
| **Assimilation** | intégrer les observations en croyances | `BeliefUpdater` |
| **Révision** | réviser la base de connaissances | `KnowledgeReviser` |

Registre clé par **catégorie** (le port devient métadonnée, plus clé) :

```
registre.register("abduction",  "ilp",    ILPEngine)       # propose des règles
registre.register("induction",  "ilp",    ILPEngine)       # généralise
registre.register("validation", "z3",     Z3Validator)     # adaptateur
registre.register("réécriture", "maude",  MaudeRewriter)
registre.register("exécution",  "maude",  MaudeExecutor)

registre.pick("validation", "z3")   # on pioche par besoin épistémique
```

Points notés :

- **Alignement natif** : `InferenceMode` encode déjà abduction / induction / déduction — la taxonomie réutilise le vocabulaire du SDK.
- **Un algo peut couvrir plusieurs catégories** (ex. Z3 : validation *et* déduction par satisfiabilité) ; c'est le registre qui déclare, pour chaque entrée, la fonction qu'il remplit.
- **Le port reste secondaire** : il apparaît comme métadonnée (quel `Protocol` est satisfait), mais n'est plus la clé de recherche.

### user

optimisation

### agent

Ajout de la catégorie **Optimisation** — et elle précise le tableau : les algorithmes génétiques / EBM ne font pas de l'*inférence logique* (abduction/induction/déduction), ils font de la **recherche / optimisation** dans l'espace des programmes.

| Catégorie (fonction) | Ce qu'elle fait | Port(s) associé(s) | Algorithmes types |
|---|---|---|---|
| **Optimisation** | chercher / optimiser dans l'espace des programmes (combiner, prioriser) | `InferenceEngine` (synthèse par recherche) | génétique, EBM, recuit simulé, descente, optimisation bayésienne |

Distinction importante :

- **Inférence logique** (abduction / induction / déduction) = *raisonner* : dériver des règles par la logique (ILP, prouveurs).
- **Optimisation** = *chercher* : explorer, composer et prioriser un espace de candidats par heuristique (génétique, EBM).

Le « mix » discuté plus haut se relit alors : `abduction (ILP) → optimisation (génétique + EBM)`. C'est le passage d'une étape logique (proposer des règles) à une étape de recherche (les combiner et les prioriser).

À noter : il n'y a pas de port « optimizer » dédié dans le SDK — l'optimisation de synthèse se branche sur `InferenceEngine`. Une éventuelle **optimisation d'expérience** (choisir l'observation la plus discriminante) serait un autre étage de la boucle, donc une autre catégorie, pas la même.

### user

C'est que, pour moi, l'optimisation et la déduction sont plus généralement des étapes de transformation intermédiaire entre l'abduction et la validation.

### agent

Exactement — ça restructure la taxonomie en **deux pôles + une couche de transformations**, plutôt qu'une liste plate :

```
Abduction ─────────[ transformations intermédiaires ]─────────> Validation
(proposer)        déduction · induction · optimisation          (juger)
                  réécriture · exécution
```

**Abduction** (produire des hypothèses) et **Validation** (confronter aux observations) sont les **bornes** de la boucle ; tout le reste est un **opérateur de transformation intermédiaire** qui raffine l'hypothèse entre sa proposition et sa confrontation au réel.

Alignement avec la boucle du SDK :

| Pôle / couche | Rôle | Étapes SDK |
|---|---|---|
| **Abduction** (origine) | produire des hypothèses | `InferenceEngine` → `Hypothesis` (`ProgramM1`) |
| **Transformations intermédiaires** | raffiner / transformer l'hypothèse | `ProgramTransformation` (réécriture), `Executor` (exécution), `ResultTransformation` — + déduction, induction, optimisation |
| **Validation** (destination) | confronter aux observations | `Validator` → `ValidationReport` |

Conséquences :

- Les catégories ne sont **plus toutes égales** : abduction et validation sont **structurelles** (les bornes), les autres sont des **opérateurs de transformation** entre les deux.
- Le SDK reflète déjà cette structure : l'invariant « transformation de programme ≠ transformation de résultat » et les ports `ProgramTransformation`/`ResultTransformation` montrent que la transformation est le cœur du chemin abduction → validation.
- « Piocher dans la lib » = choisir, pour **chaque borne et chaque transformation**, l'algo adapté — ex. abduction par ILP, optimisation par génétique, validation par Z3.

### user

Créer un plan des algos à implémenter.

### agent

Plan d'implémentation, organisé par la structure « abduction → transformations → validation » et priorisé.

**Livrable transversal** : le **registre** (`AlgorithmRegistry`) — la « lib d'algo » où chaque implémentation est enregistrée par `(catégorie, clé)`.

### Phase 1 — Fondations stdlib (faire tourner une boucle minimale sur domaine fini)

| # | Algo | Catégorie | Port | Dépendance |
|---|---|---|---|---|
| 1.1 | Réécriture de termes bornée (style Maude) | Réécriture | `ProgramTransformation`, `ReflectiveM3` | stdlib |
| 1.2 | Interpréteur fini (évaluation de `ProgramM1` sur domaine fini) | Exécution | `Executor` | stdlib |
| 1.3 | Validateur par énumération exhaustive | Validation | `Validator` | stdlib |

→ Ces trois permettent déjà `abduction → [réécriture → exécution] → validation` de bout en bout sur un domaine fini.

### Phase 2 — Synthèse

| # | Algo | Catégorie | Port | Dépendance |
|---|---|---|---|---|
| 2.1 | ILP minimal (abduction de règles candidates) | Abduction | `InferenceEngine` | stdlib (version réduite) |
| 2.2 | Algorithme génétique (combiner les règles en programmes) | Optimisation | `InferenceEngine` | stdlib |
| 2.3 | EBM / sélection évolutionnaire (prioriser les candidats) | Optimisation | `InferenceEngine` | stdlib |
| 2.4 | Pipeline « mix » ILP → génétique → EBM | Abduction + Optimisation | `InferenceEngine` composite | stdlib |

### Phase 3 — Adaptateurs optionnels (dépendances tierces, import paresseux)

| # | Algo | Catégorie | Port | Dépendance |
|---|---|---|---|---|
| 3.1 | Z3 (SMT) — validation de contraintes / contre-exemples | Validation | `Validator` (factory) | `z3-solver` |
| 3.2 | ILP complet (Popper / Metagol) | Abduction | `InferenceEngine` | tierce |
| 3.3 | MLP (réseau de neurones) — sortie non symbolique | Assimilation | adaptateur dédié | tierce |

### Hors périmètre « algo lourd » (structures, pas algorithmes)

- Assimilation directe (`BeliefUpdater`) — stdlib.
- Révision par invalidation de dépendances (`KnowledgeReviser`) — stdlib.

### Règles directrices

- **Stdlib d'abord** : la boucle minimale (phase 1) n'introduit aucune dépendance ; les adaptateurs tiers (phase 3) viennent ensuite, derrière les mêmes `Protocol`, avec import paresseux.
- **Un algo = une entrée du registre** par `(catégorie, clé)` ; le port reste une métadonnée.
- **Critère d'acceptation de chaque phase** : la boucle `Sensor → … → KnowledgeBase` doit s'exécuter de bout en bout avec les algos de la phase, sur un domaine fini démontrable (ex. langage booléen ou `nat`).

### user
