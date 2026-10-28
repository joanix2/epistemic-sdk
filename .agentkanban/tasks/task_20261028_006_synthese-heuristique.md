---
title: "Recherche inductive guidée : trous typés, beam, réparation"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Une heuristique apprise sur l’écart entre sortie attendue et sortie exécutée diminue l’explosion combinatoire "
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Une heuristique apprise sur l’écart entre sortie attendue et sortie exécutée diminue l’explosion combinatoire par rapport à l’énumération typée actuelle.

#### Protocole expérimental proposé

Implémenter expérimentalement beam/best-first bottom-up, signatures comportementales, esquisses à trous typés, recherche bidirectionnelle et réparation locale d’un programme. Apprendre éventuellement une politique de ranking sur les traces du générateur ; ablation sans réseau et sans MDL. Conserver concurrents compatibles, ne jamais confondre même signature sur M0 et équivalence prouvée.

#### Baselines et métriques

Comparer typed_search, beam uniforme, beam heuristique et beam neuronal avec budgets identiques d’évaluations ET de temps. Mesurer succès sur programmes plus profonds et familles nouvelles, coût d’inférence des heuristiques, diversité.

#### Critères de réfutation

Réfuter si la recherche guidée est plus chère ou se dégrade sur les tâches et opérateurs hors distribution.

#### Réutilisation / dépendances

Briques : typed_search.py, synthesis.py ; dépend 002 et 005.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
