---
title: "Protocole scientifique ARC, généralisation et ablations"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Une évaluation préenregistrée à coût égal permet d’identifier les vrais gains de découverte plutôt que des règ"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Une évaluation préenregistrée à coût égal permet d’identifier les vrais gains de découverte plutôt que des règles écrites à la main.

#### Protocole expérimental proposé

Geler jeux, seeds, versions M2, code, mémoire et budgets. ARC-AGI-1 training en folds de développement ; les labels publics evaluation ayant été consultés, ne pas prétendre qu’une optimisation ultérieure est validée indépendamment sur cette même évaluation. Ajouter holdout synthétique et tests de généralisation compositionnelle.

#### Baselines et métriques

Décomposer couverture par heuristiques, primitives composées, macros découvertes et apprenants humains codés en dur. Comparer au rapport 58/400 sur ARC-AGI-1 training (version compositionnelle) sans mélanger avec 100/400 et 48/400 d’anciens task_* supprimés. Mesurer coûts réels.

#### Critères de réfutation

Refuser tout résultat attribuant un gain à une brique si budget, recherche admissible ou jeu testé diffèrent sans ablation explicite.

#### Réutilisation / dépendances

Réutiliser TECHNICAL.md, ADR-009, docs/experiments ; dépend 002.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
