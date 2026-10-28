---
title: "Découverte automatique de lois M3 et règles de réécriture"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Hypothèse expérimentale à valider ou réfuter : Des régularités observées entre programmes peuvent mener à des équations généralisées et prouvées, améliorant "
---

## Conversation

### user

Inscrire cette piste du projet Epistemic SDK comme **hypothèse de recherche falsifiable**, avec validation, corroboration et critères de réfutation. Ne pas présumer qu’elle fonctionne.

### agent

**Priorité : P1. Statut : hypothèse à tester, sans implémentation engagée.**

#### Hypothèse

Des régularités observées entre programmes peuvent mener à des équations généralisées et prouvées, améliorant à leur tour les synthèses M1.

#### Protocole expérimental proposé

Générer des conjectures via anti-unification de fragments équivalents observationnellement ; chercher contre-exemples par Z3 sous théorie, ou énumération finie là où la théorie est finie. Tester préconditions des lois (translater deux fois = somme des déplacements, distributivité, symétries). Promouvoir uniquement les lois validées dans l’e-graphe.

#### Baselines et métriques

Mesurer précision des identités, contre-exemples générés, transférabilité, nombre de réécritures utiles et gain de recherche sur tâches nouvelles.

#### Critères de réfutation

Réfuter si la majorité des lois ne se généralise pas ; ne pas transformer une simple concordance sur E/S en équivalence formelle.

#### Réutilisation / dépendances

Dépend 007, 011, 012.

#### Livrables avant clôture

- [ ] Plan scientifique : hypothèses, données, budget, métriques, seuils de décision.
- [ ] Baseline reproductible et ablations à coût comparable.
- [ ] Tests/contre-exemples et conservation de la provenance M0–M3.
- [ ] Rapport : corroboration ou réfutation, limites et décision de suite.

### user
