---
title: Phase 1 — Fondations stdlib (réécriture, interpréteur, validateur)
lane: todo
created: 2026-10-15T12:30:00
updated: 2026-10-15T12:30:00
description: Implémenter les trois algorithmes stdlib de la phase 1 : réécriture de termes bornée, interpréteur fini, validateur par observation — pour faire tourner une boucle minimale sur domaine fini.
---

## Conversation

### user

Créer les tickets et implémenter.

### agent

Contrat de la phase 1 (stdlib, aucune dépendance tierce) :

| # | Fichier | Algo | Port |
|---|---|---|---|
| 1.1 | `epistemic_sdk/algorithms/rewriting.py` | `BoundedRewriter` (réécriture bornée + `matches`/`substitute`) | `ProgramTransformation` |
| 1.2 | `epistemic_sdk/algorithms/interpreter.py` | `FiniteInterpreter` (évaluation sur domaine fini, sémantique injectée) | `Executor` |
| 1.3 | `epistemic_sdk/algorithms/enumeration_validator.py` | `ObservationValidator` (confrontation sortie ↔ observations) | `Validator` |

Critère d'acceptation : la boucle `Hypothesis → [réécriture → exécution] → validation` s'exécute de bout en bout sur le langage `nat` de l'exemple, avec tests.

### user
