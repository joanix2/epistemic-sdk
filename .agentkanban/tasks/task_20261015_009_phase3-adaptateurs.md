---
title: Phase 3 — Adaptateurs optionnels (Z3, Popper, MLP)
lane: todo
created: 2026-10-15T12:30:00
updated: 2026-10-15T12:30:00
description: Adaptateurs à dépendances tierces (import paresseux) : Z3 (validation de contraintes), ILP complet (Popper/Metagol), MLP. Bloqué sur justification de dépendance par l'architecte.
---

## Conversation

### user

Créer les tickets et implémenter.

### agent

Contrat de la phase 3 — **bloqué sur dépendances tierces** :

| # | Algo | Catégorie | Dépendance |
|---|---|---|---|
| 3.1 | Z3 (SMT) — validation de contraintes / contre-exemples | Validation | `z3-solver` |
| 3.2 | ILP complet (Popper / Metagol) | Abduction | tierce |
| 3.3 | MLP (réseau de neurones) — sortie non symbolique | Assimilation | tierce |

Chaque adaptateur importe sa dépendance à la demande et implémente le même `Protocol`. Nécessite la validation de l'architecte pour ajouter la dépendance à `pyproject.toml` (règle : bibliothèque standard uniquement, sinon justification).

### user
