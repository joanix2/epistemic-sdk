---
title: Problème #4 — Invention de langage (définition automatique du M2)
lane: todo
created: 2026-10-15T14:30:00
updated: 2026-10-15T14:30:00
description: Définir automatiquement le sous-espace de recherche : quand l'espace H est épuisé (abduction), inventer un nouvel opérateur et versionner le M2.
---

## Conversation

### user

Implémenter le problème #4 : la définition automatique du sous-espace de recherche (invention de langage).

### agent

Stratégie (voir discussion) : rendre la boucle **réflexive** — traiter le `LanguageM2` comme une méta-hypothèse, ré-appliquer la boucle d'abduction un niveau au-dessus, avec score **MDL** (compression).

Étapes :
1. Hypothèse composite `H = (LanguageM2, ProgramM1)`.
2. Abstraction bottom-up : quand `P(abduire)` monte, détecter un sous-motif récurrent et le **lifter** en nouvel `Operator`.
3. Score MDL : préférer le langage qui **compresse** le plus (programmes plus courts).
4. Réflexion (M3) : réutiliser les moteurs au niveau méta via `ReflectiveM3`.

**Premier pas (ce ticket)** : le mécanisme de lifting — `LanguageExtender` qui ajoute un opérateur (défini par une expression) à un `LanguageM2` versionné. La détection de motif récurrent (pattern mining) et le score MDL sont les étapes suivantes.

### user

### agent

2026-10-16 — Reprise sur l'objectif explicite : améliorer la résolution ARC pour éprouver l'architecture épistémique. La direction retenue par l'utilisateur remplace la proposition précédente de langage isolé : chaque M2 de tâche spécialise un nœud d'une taxonomie partagée ; les abstractions réutilisables conservent portée, version et provenance. Aucun changement des exports publics ni commit prévu.

Plan d'intégration : (1) recherche typée choisissant le programme sur les seuls exemples d'entraînement ; (2) primitives d'objets et complétion de symétrie internes ; (3) taxonomie versionnée avec héritage et définitions exécutables ; (4) apprentissage de macros à partir des solutions d'entraînement, mémoire figée avant évaluation ; (5) comparaison reproductible primitives globales / bibliothèque plate / taxonomie et transfert. Mesurer séparément training et evaluation ARC ; ne pas présenter ces données publiques comme un score officiel privé ARC Prize.

Délégations coordonnées : ARC-OBJECTS possède uniquement `algorithms/grid_objects.py` et ses tests ; ARC-TAXONOMY possède uniquement `algorithms/language_taxonomy.py` et ses tests. L'architecte intègre recherche, adaptateur, mesure, documentation et tests bout en bout. Les fichiers non suivis préexistants sont préservés.

### user

### agent

2026-10-16 — Intégration et audit terminés pour l'objectif d'amélioration ARC.

Modifications : recherche typée `LanguageDiscovery.fit` sans accès aux réponses test ; objets et transformations internes ; DAG de familles M2 versionnées ; spécialisations par tâche ; admission et sérialisation de définitions avec provenance ; réutilisation et héritage explicite ; harness de comparaison et audit indépendant des prédictions. Aucun export public modifié, aucune dépendance ni commit ajouté. L'ancien fichier non suivi `language_extender.py` est préservé.

Résultats vérifiés sur 400 tâches par ensemble :

| Mode | Développement | Évaluation publique séparée |
|---|---:|---:|
| Global | 16 | 1 |
| Plat | 20 | 2 |
| Taxonomie | 26 | 4 |
| Plat + mémoire figée | non mesuré | 3 |
| Taxonomie + mémoire figée | non mesuré | 4 |

Dix gains et aucune perte face au global sur le développement ; trois gains et aucune perte sur l'évaluation. Huit définitions apprises à partir des seules démonstrations source. Une définition de sélection du plus grand objet est transférée à une autre tâche : recherche plate 5 000 candidats sans solution → neuf candidats avec solution ; recherche taxonomique 207 → 190 candidats, déjà résolue sans mémoire. La mémoire ne produit donc aucun gain supplémentaire de couverture pour la taxonomie et augmente légèrement son coût total en candidats. Les deux contrôles avec mémoire utilisent exactement la même empreinte.

Validation : 150 tests réussis, Ruff, mypy (133 fichiers avec le script d'audit), harness check des 41 exports, exemple nat et git diff --check réussis. Les prédictions et statuts archivés ont été recomparés aux données, les empreintes et liens de validation audités. La revue contradictoire a détecté puis fait corriger le contournement des limites intermédiaires par les macros et l'absence de plafond des sous-termes. Tests de régression présents. Le seul nettoyage post-mesure est une ligne vide finale ; l'équivalence AST et les empreintes avant/après sont archivées.

Limites : scores publics ARC-AGI-1, pas un résultat officiel privé ARC Prize ; taxonomie et politique initiales manuelles ; ablation mêlant structure, ordre et espaces de recherche ; budget de candidats différent d'un coût machine ; aucune démonstration de généralité universelle ni de boucle complète de révision. Les défauts historiques e-graph/ILP/ASP/révision booléenne restent hors de ce chemin d'exécution. L'ancien plan M3 réflexif n'a pas été implémenté : il est remplacé pour cette expérience par la direction utilisateur de taxonomie partagée, sans prétendre résoudre le problème général #4.

Rapport, artefacts et commandes : `docs/experiments/arc-taxonomy/REPORT.md`, `comparison.json`, `memory.json`, `TECHNICAL.md`. `PROGRESS.md`, `STATE.md`, la mémoire Kanban et ADR-007 sont actualisés. Objectif du fil atteint : score amélioré et transfert/choix de langage éprouvés par une expérience reproductible avec résultats positifs et négatifs explicites.

### user
