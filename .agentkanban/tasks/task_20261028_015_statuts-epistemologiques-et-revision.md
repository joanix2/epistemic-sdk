---
title: "Croyances/ontologie et révision de dépendances en cascade"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : La provenance formelle des croyances, conjectures et abstractions permet de rétracter correctement toute conna"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P1. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

La provenance formelle des croyances, conjectures et abstractions permet de rétracter correctement toute connaissance devenue invalide après un contre-exemple.

#### Protocole expérimental proposé

Construire graphe d’arguments, niveaux candidate/compatible/corroborated/refuted/proved/inconclusive, version des observations, dépendances des programmes et M2 dérivés. Conserver la trace des contre-exemples, replay JSONL et réparation incrémentale après rétractation.

#### Baselines et métriques

Injecter contre-exemple tardif dans tâche où plusieurs opérateurs M2 sont promus ; vérifier invalidation complète, conservation des croyances indépendantes et recalcul minimal.

#### Critères de réfutation

Réfuter si validation sur entraînement est stockée comme preuve, si les dépendances sont perdues ou si une révision efface sans provenance.

#### Réutilisation / dépendances

Dépend 001 ; compléter KnowledgeReviser et la mémoire existante, pas créer une ontologie parallèle.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
