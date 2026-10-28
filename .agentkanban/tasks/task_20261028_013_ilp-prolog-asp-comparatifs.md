---
title: "Induction relationnelle : ILP, Popper, Prolog, ASP comparés"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : L’induction de relations logiques avec biais de modes/métarègles pourrait synthétiser certaines règles ARC à m"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P1. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

L’induction de relations logiques avec biais de modes/métarègles pourrait synthétiser certaines règles ARC à moins de candidats que la recherche de termes.

#### Protocole expérimental proposé

Auditer ilp.py, popper_ilp.py, asp_synthesis.py et défauts documentés ; comparer unification, SLD, récursion, négation et clauses de sélection avec typed_search sur booléen, objets et relations left_of, connected, same_shape. Descriptifs et exemples de relations disponibles identiques entre algorithmes.

#### Baselines et métriques

Mesurer exactitude OOD, nombre de clauses, paramètres et temps, robustesse bruit, coût des templates. Ablations métarègles et nombre d’exemples.

#### Critères de réfutation

Réfuter si une méthode exploite des labels relationnels absents en situation réelle ou ne bat pas une baseline sérieuse.

#### Réutilisation / dépendances

Ticket task_20261015_004_algorithmes.md inclut déjà ILP/GA/EBM ; ici hypothèse comparative et tests contradictoires.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
