---
title: Phase 2 — Synthèse (ILP, génétique, EBM, pipeline mix)
lane: todo
created: 2026-10-15T12:30:00
updated: 2026-10-15T12:30:00
description: Implémenter les algorithmes de synthèse stdlib : ILP minimal (abduction), algorithme génétique (combiner), EBM (prioriser), et le pipeline mix ILP → génétique → EBM.
---

## Conversation

### user

Créer les tickets et implémenter.

### agent

Contrat de la phase 2 (stdlib) :

| # | Algo | Catégorie | Port |
|---|---|---|---|
| 2.1 | ILP minimal (abduction de règles) | Abduction | `InferenceEngine` |
| 2.2 | Algorithme génétique (combiner) | Optimisation | `InferenceEngine` |
| 2.3 | EBM / sélection évolutionnaire (prioriser) | Optimisation | `InferenceEngine` |
| 2.4 | Pipeline « mix » ILP → génétique → EBM | Abduction + Optimisation | `InferenceEngine` composite |

Dépendance : phase 1 (fondations). À faire après la phase 1.

### user
