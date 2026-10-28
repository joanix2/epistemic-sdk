---
title: "Algèbres alternatives : tropicale, p-adique, équivariance apprise"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Des géométries spéciales peuvent fournir des biais inductifs utiles, mais leur intérêt pour la synthèse symbol"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P3. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Des géométries spéciales peuvent fournir des biais inductifs utiles, mais leur intérêt pour la synthèse symbolique n’est pas démontré.

#### Protocole expérimental proposé

Tester séparément max-plus/logsumexp à température apprise sur problème de programmation dynamique, ultramétrique p-adique sur AST hiérarchiques, et symétries apprises vs groupes fixes sur transformations ARC. Ne pas assembler les trois idées avant mesures individuelles.

#### Baselines et métriques

Baselines euclidiennes et réseaux équivariants ; mesurer généralisation hors distribution, coût, sensibilité graines et qualité des représentations.

#### Critères de réfutation

Réfuter sans gain robuste ou si la performance est due à une capacité/paramétrisation différente. Recherche exploratoire, pas prérequis.

#### Réutilisation / dépendances

Dépend 002 et 008.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
