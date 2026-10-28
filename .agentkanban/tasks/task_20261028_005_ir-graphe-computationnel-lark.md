---
title: "Graphe computationnel M1 : IR typée, DAG et DSL Lark"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Une IR de graphe typé partage les sous-expressions et rend la recherche, la croissance et la réécriture intero"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Une IR de graphe typé partage les sous-expressions et rend la recherche, la croissance et la réécriture interopérables tout en conservant un programme M1 lisible.

#### Protocole expérimental proposé

Proposer conversions Term M3 ↔ AST ↔ DAG, nœuds, ports, typage, identifiants stables, sortie, exécuteur, gestion des cycles et représentation sérialisée. Essayer Lark pour un DSL de surface seulement ; IR canonique indépendante du parseur. Évaluer igraph comme bibliothèque de graphe si utile, sans le confondre avec e-graph.

#### Baselines et métriques

Tester round-trip, préservation sémantique, CSE, version M2, provenance et coût mémoire/temps arbre vs DAG. Définir limites des graphes récurrents avant d’en autoriser.

#### Critères de réfutation

Réfuter si la conversion change la sémantique, si les cycles non définis passent, ou si le graphe devient inutilement plus coûteux que les termes existants.

#### Réutilisation / dépendances

M1, M2 et M3 existants ; aucune modification des 41 exports publics sans ADR.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
