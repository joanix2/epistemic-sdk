---
title: "Graphes de relations, morphismes M2 et équivalence structurelle"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Les morphismes typés entre schémas M2 permettent des traductions et transferts de concepts sans coder chaque a"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P2. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Les morphismes typés entre schémas M2 permettent des traductions et transferts de concepts sans coder chaque adaptation domaine par domaine.

#### Protocole expérimental proposé

Définir M1 avec composition AST + graphe de relations transversales (IDs/arêtes). Proposer homomorphismes/transductions M2→M2′ vérifiés par contraintes SMT et, pour cardinalités, flot inférieur/maximum lorsque pertinent. Étudier bisimulation et préservation d’invariants ; générer un contre-exemple de migration lorsqu’elle échoue.

#### Baselines et métriques

Benchmarks schémas synthétiques avec ajouts/suppressions de relations et contraintes de cardinalité, coûts de solveur, correction des migrations et taux de cas indécidables.

#### Critères de réfutation

Réfuter si le passage entre langages ne préserve pas les propriétés, ou si on généralise abusivement des garanties de cardinalité à des invariants riches.

#### Réutilisation / dépendances

Axe M3/M2 lié aux discussions F-algèbres et transformations de schémas, non indispensable au prototype ARC.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
