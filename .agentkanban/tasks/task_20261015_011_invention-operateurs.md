---
title: Invention d'opérateurs (abstraction discovery)
lane: todo
created: 2026-10-15T13:00:00
updated: 2026-10-15T13:00:00
description: Premier pas concret du problème #4 — lifter une sous-expression en nouvel opérateur, versionner le M2.
---

## Conversation

### user

Créer des tickets et implémenter (problème #4).

### agent

Contrat : `OperatorInvention.lift(term, language, operator_name)` — extrait les variables libres d'un terme, crée un `Operator` (arité = nombre de variables libres), ajoute un `Axiom` de définition `op(vars) = term`, et incrémente la version du `LanguageM2`. C'est la brique qui permet à la boucle « abduire » de *construire* un nouvel opérateur (au lieu de seulement signaler l'épuisement de l'espace `H`).

### user
