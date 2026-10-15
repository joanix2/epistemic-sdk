---
title: Cas d'étude : algèbre booléenne
lane: todo
created: 2026-10-15T11:22:52
updated: 2026-10-15T11:22:52
description: Premier cas d'étude complet sur l'algèbre booléenne (M2 déclaré, tables, lois, découverte de programmes).
---

## Conversation

### user

Commencer par un cas d'étude : l'algèbre booléenne.

### agent

Ticket créé. Objectif : cas d'étude fondateur — déclarer l'algèbre booléenne M2 (constantes, NOT, AND, OR, lois), les tables finies, et démontrer la découverte de programmes booléens (ex. XOR) avec les instances d'algorithmes.

### user

Expérience 001 — Découverte d'un opérateur booléen inconnu à partir de 3 observations, en utilisant toute la boucle épistémologique du SDK. Boîte noire déterministe `f: Bool × Bool → Bool`. 3 observations d'entraînement `(F,F)→F`, `(F,T)→T`, `(T,T)→F` + 1 observation de validation indépendante `(T,F)→T`. Le moteur doit découvrir XOR parmi `{AND, OR, XOR, NAND, NOR, XNOR}` sans coder la réponse en dur, via : M2 booléen (sortes/opérateurs/axiomes de table de vérité + `not(not(X))=X`), Sensor, BeliefUpdater, InferenceEngine (6 candidats, élimination par exécution), ProgramTransformation (`not(not(op(A,B))) → op(A,B)`), Executor, Validator (ajustement vs indépendant), KnowledgeReviser, orchestration `EpistemicEngine`. Livrables dans `examples/boolean_operator_discovery/` + tests + démo `python -m examples.boolean_operator_discovery`. Résultat attendu : XOR, avec prédiction correcte sur la 4e observation.

### agent

Plan : implémenter le cas d'étude complet dans `examples/boolean_operator_discovery/` (un fichier par responsabilité), en réutilisant la Phase 1 (`FiniteInterpreter`, `ObservationValidator`, `matches`/`substitute`) plutôt qu'en dupliquant. Composants : `boolean_language.py` (LanguageM2 + axiomes + sémantique), `sensor.py`, `belief_updater.py`, `inference.py`, `transformation.py`, `interpreter.py`, `validator.py`, `knowledge_reviser.py`, `engine.py`, `__main__.py`, `README.md` + `tests/test_boolean_discovery.py`.

### user

continue

### agent

Expérience 001 **terminée, vérifiée et commitée**. Rapport final (section 17 du cahier des charges) :

**1. Ce qui fonctionne** — la boucle complète s'exécute de bout en bout :
- `Sensor` → 3 observations d'entraînement + 1 de validation, provenance conservée.
- `BeliefUpdater` → 3 croyances `f(a,b)=output` + relations `SUPPORTS`.
- `InferenceEngine` → 6 candidats `not(not(op(A,B)))`, élimination par exécution via `ProgramRunner`.
- `ProgramTransformation` → `not(not(X)) → X`, sémantique préservée (vérifiée sur les 4 cas × 6 opérateurs).
- `Executor` → `FiniteInterpreter` (réutilisé) + `ProgramRunner`.
- `Validator` → ajustement (entraînement) vs validation indépendante (4e observation jamais vue par l'inférence).
- `KnowledgeReviser` → 1 connaissance active avec provenance complète.
- **Résultat : XOR découvert, prédiction `(T,F)→T` correcte, statut `corroborated`.**

**2. Modifications du SDK** — **aucune interface publique modifiée**. L'expérience réutilise la Phase 1 (`FiniteInterpreter`, `matches`/`substitute`) et ajoute ses composants dans `examples/`. Seule nuance : un `BooleanValidator` dédié (voir anomalie 1).

**3. Ce qui reste à implémenter** — le moteur réflexif M3/Maude (`ReflectiveM3`) n'est pas implémenté ; l'interpréteur évalue via sémantique injectée (autorisé). La découverte reste une **identification dans un catalogue** (6 opérateurs fixés), pas de la **synthèse** (primitives AND/OR/NOT seules) — c'est l'expérience 002 envisagée.

**4. Limites scientifiques constatées** — 3 observations suffisent à identifier un opérateur dans la famille des 6, mais PAS parmi les 16 fonctions booléennes (subtilité anticipée). Domaine fini et sans bruit : la 4e observation couvre la dernière combinaison, établissant l'équivalence extensionnelle sur le domaine binaire complet — pas une preuve hors domaine.

**5. Anomalies d'architecture révélées** —
1. `ObservationValidator` (Phase 1) compare `result.output` à `obs.value` en entier ; l'expérience a dû introduire un `BooleanValidator` car la valeur d'observation est un `BooleanSample` structuré (a, b, output). Signe que le validateur générique suppose une valeur atomique.
2. `FiniteInterpreter` retourne `Any` (compatible `bool` mais sans typage fort) — précision de type perdue au passage du port.

**Tests** : `tests/test_boolean_discovery.py` (13 tests d'acceptation) — opérateurs, mal-typage, provenance, relations, programmes M1, transformation, ProgramRunner, réfutation, non-fuite validation, découverte XOR, connaissance, déterminisme. **46/46 tests passent au total.**

### user
