---
title: "Neurogenèse : Graph NCA et croissance de programmes M1"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Un automate neuronal sur graphe créant/différenciant/supprimant des nœuds apprend des architectures computatio"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P1. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Un automate neuronal sur graphe créant/différenciant/supprimant des nœuds apprend des architectures computationnelles qui généralisent mieux que la génération séquentielle.

#### Protocole expérimental proposé

État neuronal par nœud, échange local de messages, actions spawn/connect/differentiate/replace/prune, contraintes de typage et de DAG. Entraîner d’abord par imitation de traces de recherche, puis optimiser par sélection/RL si nécessaire. Décodage en Term M1 exécutable et validation Z3 indépendante. Tester avec et sans phéromones/signaux diffusifs comme canal informationnel.

#### Baselines et métriques

Comparer GRU génératif, beam symbolique, GNN sans croissance, Graph NCA avec croissance sur circuits booléens puis transformations ARC. Mesurer exactitude cachée, extrapolation taille, budget, réutilisation de modules, ablations spawn/prune.

#### Critères de réfutation

Réfuter si la croissance ne produit aucun gain robuste ou seulement des motifs visuels non sémantiques. Neurogenèse = hypothèse, pas fonction démontrée.

#### Réutilisation / dépendances

Dépend 002, 005, 006 ; plan distinct des NCA de transformation directe des grilles.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
