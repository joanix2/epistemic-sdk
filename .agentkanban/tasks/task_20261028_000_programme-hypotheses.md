---
title: "Backlog scientifique : hypothèses transdisciplinaires M0–M3"
lane: todo
created: 2026-10-28T21:25:00+01:00
updated: 2026-10-28T21:25:00+01:00
description: "Programme de recherche falsifiable : perception, CEGIS, langages, graphes, méta-algèbre et généralisation."
---

## Conversation

### user

Ajouter les sujets discutés dans ChatGPT et manquants/non intégrés dans le dépôt, notamment VSA, boucle CEGIS, e-graphes, induction, méta-algèbre, ILP, MLN et neurogenèse. Tous doivent rester des hypothèses à tester.

### agent

Backlog de recherche du 28 octobre 2026. Aucun développement scientifique n’est engagé par cette création de tickets. Priorités : P0 infrastructure et expériences déterminantes, P1 hypothèses majeures, P2 extensions, P3 spéculatif.

## Règles communes

- Préenregistrer hypothèse, baselines, coût de calcul, partition de données, métriques, seuils et conditions d’échec avant implémentation.
- Ne pas confondre ajustement sur M0, corroboration sur observations indépendantes, preuve d’équivalence sous théorie et vérité générale.
- Ne jamais merger deux e-classes sur la seule égalité des sorties du dataset.
- Garder distincts objets (R / perception), ontologie/croyances, M2 (DSL et taxonomie), M1 (programmes), M3 (algèbres), M0 (E/S).
- Ne pas écrire en dur de solutions complexes pour faire monter un score ARC ; se conformer à AGENTS.md et ADR-009.
- L’évaluation ARC-AGI-1 publique a déjà été examinée : après optimisation, ne plus la présenter comme validation indépendante. Utiliser des tests réservés et des ablations.
- Rapporter aussi les résultats négatifs et les hypothèses réfutées, et conserver provenance et contre-exemples.
- Respecter plan → todo → implement dans Agent Kanban. Ce backlog ne déclenche pas lui-même le développement.

## Tickets de recherche (ordre des dépendances dans les fichiers)

- **P0** [CEGIS épistémologique complet M0–M3](task_20261028_001_cegis-epistemologique.md)
- **P0** [Dataset graphes M1 → paires E/S, contre-exemples et OOD](task_20261028_002_jeu-de-donnees-programmes-graphes.md)
- **P0** [Perception multi-hypothèses et ontologies de scène](task_20261028_003_perception-ontologies-concurrentes.md)
- **P0** [Vector Symbolic Algebras (VSA/HRR/SSP) hybrides pour ARC](task_20261028_004_algebres-vectorielles-ssp.md)
- **P0** [Graphe computationnel M1 : IR typée, DAG et DSL Lark](task_20261028_005_ir-graphe-computationnel-lark.md)
- **P0** [Recherche inductive guidée : trous typés, beam, réparation](task_20261028_006_synthese-heuristique.md)
- **P0** [E-graphes : audit, preuves et intégration au solveur ARC](task_20261028_007_egraphe-audit-integration.md)
- **P0** [Protocole scientifique ARC, généralisation et ablations](task_20261028_008_protocole-benchmark-arc.md)
- **P1** [Co-induction (R, L, P) : perceptions, langages M2 et M1](task_20261028_009_coinduction-representation-langage-programme.md)
- **P1** [Neurogenèse : Graph NCA et croissance de programmes M1](task_20261028_010_neurogenese-graph-nca.md)
- **P1** [DreamCoder-like : abstraction, compression MDL et transfert](task_20261028_011_abstractions-iteratives-mdl.md)
- **P1** [M3 : réflexivité Maude, métalgèbres, morphismes et F-algèbres](task_20261028_012_m3-meta-algebre-reflexive.md)
- **P1** [Induction relationnelle : ILP, Popper, Prolog, ASP comparés](task_20261028_013_ilp-prolog-asp-comparatifs.md)
- **P1** [Contrôleur expérimental actif : désaccord, entropie, P(H)/P(E)](task_20261028_014_selection-active-experiences.md)
- **P1** [Croyances/ontologie et révision de dépendances en cascade](task_20261028_015_statuts-epistemologiques-et-revision.md)
- **P1** [Découverte automatique de lois M3 et règles de réécriture](task_20261028_016_induction-lois-meta-algebriques.md)
- **P2** [Markov Logic Networks (MLN) et logique probabiliste des croyances](task_20261028_017_markov-logic-networks.md)
- **P3** [Algèbres alternatives : tropicale, p-adique, équivariance apprise](task_20261028_018_algebres-tropicales-padiques-symetries.md)
- **P2** [Émergence transdisciplinaire comme inducteur de structures](task_20261028_019_emergence-sciences-complexes.md)
- **P2** [Graphes de relations, morphismes M2 et équivalence structurelle](task_20261028_020_morphismes-graphes-m2.md)

## Existant et points à ne pas dupliquer

- Modules existants : `algorithms/egraph.py`, `typed_search.py`, `language_discovery.py`, `language_taxonomy.py`, `z3_validator.py`, `ilp.py`, `popper_ilp.py`, `asp_synthesis.py`, `active_loop.py`, `grid_objects.py`.
- Tickets historiques : `task_20261015_004_algorithmes`, `task_20261015_011_invention-langage`, `task_20261015_012_definition-auto-m2`, `task_20261015_013_egraphe`, tests de réfutation.
- Les résultats `48/400` et `100/400` issus des apprenants `task_*` sont archivés mais le code a été supprimé par ADR-009 ; l’expérience compositionnelle a un fichier `training-taxonomy-composed.json` à 58/400.

### user
