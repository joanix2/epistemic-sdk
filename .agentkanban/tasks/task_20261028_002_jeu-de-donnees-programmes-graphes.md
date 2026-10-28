---
title: "Dataset graphes M1 → paires E/S, contre-exemples et OOD"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Un générateur de programmes typés et de observations incomplètes fournit un benchmark contrôlé pour apprendre "
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Un générateur de programmes typés et de observations incomplètes fournit un benchmark contrôlé pour apprendre à reconstruire des graphes et mesurer l’identifiabilité.

#### Protocole expérimental proposé

Échantillonner des M1 AST/DAG à partir de grammaires M2, exécuter sur des entrées variées, conserver programme source, sémantique, E/S, contre-exemples et transformations équivalentes. Partager par fonction sémantique, pas seulement par syntaxe. Familles : booléens, automates finis, objets ARC spatiaux. Oracle limité aux données synthétiques.

#### Baselines et métriques

Splits train/validation/test par fonctions et familles, puis extrapolation profondeur (≤4 portes → 5–8), opérateurs/compositions inédites. Baselines énumération, GRU, MLP, ILP et beam. Mesures : exactitude cachée, candidats, temps, complexité, couverture, abstention.

#### Critères de réfutation

Réfuter la qualité du benchmark en cas de fuite sémantique, de répétition de fonctions entre partitions ou de score obtenu sans généralisation.

#### Réutilisation / dépendances

Infrastructure nouvelle ; réutiliser les interpréteurs et les contrats M0/M1 existants.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
