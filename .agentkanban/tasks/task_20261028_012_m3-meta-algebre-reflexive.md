---
title: "M3 : réflexivité Maude, métalgèbres, morphismes et F-algèbres"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Un noyau M3 généralisable permet de construire des DSL M2, exécuter/transformer des programmes par réflexion e"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P1. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Un noyau M3 généralisable permet de construire des DSL M2, exécuter/transformer des programmes par réflexion et vérifier des lois algébriques sans cas particuliers.

#### Protocole expérimental proposé

Tester quote/unquote, méta-exécution de termes, application d’équations/règles, génération M2 depuis signatures et lois et homomorphismes de F-algèbres. Comparer M1 direct et interprété au métaniveau ; prototype symbolique minimal booléen/naturel, puis géométrie. Ajouter selon besoin contraintes de relation/cardinalité Z3.

#### Baselines et métriques

Tests de correspondance sémantique quote/eval, invariants de typage, préservation des opérations par morphisme et contre-exemples SMT. Documenter ce qui reste un contrat non exécuté.

#### Critères de réfutation

Réfuter si seules des opérations bricolées par domaine passent ; ne pas prétendre posséder un moteur Maude complet.

#### Réutilisation / dépendances

Réutiliser m3/ et ReflectiveM3 ; ADR-003 explicite les limites actuelles.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
