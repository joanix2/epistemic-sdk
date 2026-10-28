---
title: "E-graphes : audit, preuves et intégration au solveur ARC"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Des e-graphes corrects et pilotés par des équivalences justifiées réduisent les redondances de recherche et fa"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Des e-graphes corrects et pilotés par des équivalences justifiées réduisent les redondances de recherche et facilitent l’abstraction à budget égal.

#### Protocole expérimental proposé

Auditer egraph.py : gestion des classes après merge, IDs, hashcons, congruence, e-matching, cycles, saturation bornée, extraction, règles conditionnelles ; tester spécialement les IDs créés via len(_classes) après fusion. Garder espace d’hypothèses compatibles distinct des e-classes prouvées. Comparer à un adaptateur egg/egglog si besoin.

#### Baselines et métriques

Tests adversariaux De Morgan, réécritures erronées, merges répétés ; comparer solveur sans e-graphe, avec e-graphe, avec signatures observationnelles et avec les deux. Métriques : exactitude, RAM, temps, candidats et validité des fusions.

#### Critères de réfutation

Réfuter si faux regroupements ou absence de bénéfice réel après coût de maintenance.

#### Réutilisation / dépendances

Ticket existant task_20261015_013_egraphe.md couvre le noyau ; ceci cible audit, garanties et intégration.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
