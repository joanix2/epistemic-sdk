---
title: "Contrôleur expérimental actif : désaccord, entropie, P(H)/P(E)"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Les requêtes choisies pour départager des programmes compatibles réduisent les observations nécessaires et ori"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P1. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Les requêtes choisies pour départager des programmes compatibles réduisent les observations nécessaires et orientent quand tester, explorer ou abduire.

#### Protocole expérimental proposé

Exécuter ActiveLoop, EntropySelector, BayesianUpdater et sélecteur par désaccord sur oracle synthétique ; conserver propositions réfutées et nouvelles observations. Proposer politique de sélection avec coût de requêtes et option d’abstention. Pour ARC public, aucun accès à oracle de sortie cachée.

#### Baselines et métriques

Comparer aléatoire, corroboration pure, désaccord, entropie et stratégie apprise. Mesurer requêtes, taux exact final, calibration, coût et cas indéterminés.

#### Critères de réfutation

Réfuter si la politique informée n’aide pas à budget égal, ou si elle dépend d’un oracle inexistant sur la tâche cible.

#### Réutilisation / dépendances

Dépend 001, 002 et 015 ; contrôleur partiel existant à intégrer.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
