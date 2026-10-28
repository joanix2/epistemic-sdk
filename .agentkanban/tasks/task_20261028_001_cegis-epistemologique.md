---
title: "CEGIS épistémologique complet M0–M3"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Conserver plusieurs programmes/ontologies/langages candidats, rechercher des contre-exemples et réviser les cr"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Conserver plusieurs programmes/ontologies/langages candidats, rechercher des contre-exemples et réviser les croyances donne une meilleure généralisation que sélectionner un seul M1 compatible avec M0.

#### Protocole expérimental proposé

Connecter Sensor→Observation→BeliefGraph→abduction→M1/M2→ProgramRunner→Z3/fini→KnowledgeReviser→nouvelle induction. Construire une trace complète et rejouable. En cas de réfutation, diagnostiquer erreur de paramètre M1, structure M1, représentation perceptive ou expressivité M2. Conserver les candidats concurrents.

#### Baselines et métriques

Comparer solveur one-shot, CEGIS à oracle synthétique et CEGIS avec observation passive. Mesurer exactitude hors exemples, requêtes oracle, coût et erreurs de révision. Sur ARC caché, aucune requête à la vérité test.

#### Critères de réfutation

Échec si aucune amélioration à budget comparable, ou si le résultat dépend de données test non disponibles. Distinguer sat sur exemples, corroboration indépendante et validité universelle sous théorie.

#### Réutilisation / dépendances

Briques existantes : active_loop.py, epistemic_engine.py (Protocol), z3_validator.py, validators, belief graph. Ne pas en recréer de versions parallèles.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
