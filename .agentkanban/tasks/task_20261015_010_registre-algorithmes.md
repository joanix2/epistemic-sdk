---
title: Registre d'algorithmes (lib d'algo)
lane: todo
created: 2026-10-15T12:30:00
updated: 2026-10-15T12:30:00
description: Implémenter le AlgorithmRegistry — catalogue clé par (catégorie, clé) où chaque implémentation est enregistrée par fonction épistémique, le port n'étant qu'une métadonnée.
---

## Conversation

### user

Créer les tickets et implémenter.

### agent

Contrat : `epistemic_sdk/algorithms/registry.py` — classe `AlgorithmRegistry` avec `register(category, key, impl)` et `pick(category, key)`. Catégories = fonctions épistémiques (abduction, induction, déduction, optimisation, validation, réécriture, exécution, assimilation, révision). Le port reste une métadonnée, pas la clé. Enregistre les implémentations des phases 1 et 2.

### user
