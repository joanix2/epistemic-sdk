---
title: "Vector Symbolic Algebras (VSA/HRR/SSP) hybrides pour ARC"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Une algèbre de vecteurs symboliques spatiaux améliore appariement, transfert de translations et guidage de syn"
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P0. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Une algèbre de vecteurs symboliques spatiaux améliore appariement, transfert de translations et guidage de synthèse sans sacrifier l’exécution exacte sur les objets symboliques.

#### Protocole expérimental proposé

Tester HRR : superposition, liaison par convolution circulaire FFT, unbinding et mémoire de nettoyage ; SSP : encodage positionnel, translation par binding et formes relatives au centre. Représenter O=(objet symbolique exact, vecteur VSA). Comparer aux coordonnées/masques et aux embeddings standards ; investiguer collisions et résolution.

#### Baselines et métriques

Mesurer précision de décodage, similarité des formes, top-k d’appariements, généralisation à nouvelles positions, coût dimensionnel (128/512/1024), temps et gain pour la synthèse. Tests sur objets multicolores et bruit.

#### Critères de réfutation

Réfuter si la VSA ne bat pas une baseline simple à coût comparable ou si des approximations faussent le résultat symbolique.

#### Réutilisation / dépendances

Référence à vérifier : Joffe/Eliasmith, Vector Symbolic Algebras for ARC (2026). Dépend 002 et 003.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
