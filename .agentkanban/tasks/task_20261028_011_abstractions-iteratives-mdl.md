---
title: "DreamCoder-like : abstraction, compression MDL et transfert"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Découvrir des sous-graphes récurrents et les promouvoir en opérateurs M2 réutilisables réduit le coût de reche"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P1. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Découvrir des sous-graphes récurrents et les promouvoir en opérateurs M2 réutilisables réduit le coût de recherche futur, à condition de contrôler les macros inutiles.

#### Protocole expérimental proposé

Explorer anti-unification, e-classes prouvées et score MDL intégrant longueur totale du langage+programmes+coût de recherche. Versionner chaque nouvelle primitive, conserver provenance de ses tâches sources et invalider si réfutée. Contrôler transfert vers tâches indépendantes.

#### Baselines et métriques

Comparer baseline sans mémoire, macros arbitraires, macros MDL et registre existant. Mesurer précision sur nouvelles fonctions, réduction de candidats, inflation du DSL et gains OOD.

#### Critères de réfutation

Réfuter si les nouveaux opérateurs élargissent la recherche plus qu’ils ne la facilitent ; ne pas promouvoir de fonctions complexes écrites à la main.

#### Réutilisation / dépendances

Complète les modules abstraction_discovery, operator_invention et ticket historique d’invention M2.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
