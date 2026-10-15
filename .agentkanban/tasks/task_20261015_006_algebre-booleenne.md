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
