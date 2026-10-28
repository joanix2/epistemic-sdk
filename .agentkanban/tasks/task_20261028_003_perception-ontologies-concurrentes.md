---
title: "Perception multi-hypothèses et ontologies de scène"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : L’induction de représentations de scènes concurrentes (pixels, objets, relations) augmente la résolution de tâ"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

L’induction de représentations de scènes concurrentes (pixels, objets, relations) augmente la résolution de tâches ARC qui ne partagent pas une segmentation fixe.

#### Protocole expérimental proposé

Produire plusieurs représentations candidate : grille brute, composantes connexes 4/8, objets multicolores, régions, groupes, hiérarchies, relations spatiales et topologiques. Proposer fusion/scission d’entités ; lier chaque hypothèse à M0 et BeliefGraph, conserver supports et contre-exemples. Distinguer descripteurs fournis et ontologie réellement découverte.

#### Baselines et métriques

Comparer segmentation fixe, multi-hypothèses, choix de représentation appris et oracle de représentation sur scènes synthétiques tenues hors distribution. Mesurer rappel objets/relations, erreur de transformation, temps et nombre de candidats.

#### Critères de réfutation

Réfuter si multiplication des segmentations augmente la recherche sans gain ou si les concepts exigent des annotations cachées non disponibles.

#### Réutilisation / dépendances

Réutiliser grid_objects.py et la taxonomie M2 ; ne pas appeler « découverte » des primitives décrites manuellement.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
