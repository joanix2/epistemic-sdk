---
title: "Markov Logic Networks (MLN) et logique probabiliste des croyances"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Les MLN peuvent représenter mieux que des confidences indépendantes les régularités relationnelles incertaines"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P2. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Les MLN peuvent représenter mieux que des confidences indépendantes les régularités relationnelles incertaines et les contradictions locales.

#### Protocole expérimental proposé

Prototyper petit graphe d’objets/relations avec clauses pondérées et probabilités calibrées, puis comparer à Bayes indépendant, scores heuristiques et contraintes SMT dures ; évaluer MAP et marges sur petit domaine avant toute bibliothèque externe. Ne pas confondre logique floue, probabilité et preuve.

#### Baselines et métriques

Mesurer Brier/NLL, calibration, précision sur règles cachées, temps/mémoire et complexité selon nombre d’objets/clauses.

#### Critères de réfutation

Réfuter si le coût est prohibitif ou si des poids MLN masquent des contradictions et sont traités comme vérités démontrées.

#### Réutilisation / dépendances

Dépend 003, 015 ; hypothèse alternative, ne pas imposer MLN au noyau.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
