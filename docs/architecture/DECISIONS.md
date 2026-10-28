# Décisions architecturales (ADR)

Journal des décisions structurantes. Format : numéro, date, statut, contexte, décision, conséquences. Toute modification de signature d'une interface publique d'`epistemic_sdk/__init__.py` doit être consignée ici et validée par l'architecte.

## ADR-001 — Découpage du paquet `epistemic_sdk`

- **Date** : 2026-10-15 — **Statut** : accepté.
- **Contexte** : le SDK doit distinguer les quatre niveaux M0–M3 et la boucle épistémologique.
- **Décision** : découper en sous-paquets `m3`, `m2`, `m1`, `observations`, `beliefs`, `inference`, `execution`, `validation`, `knowledge`, `engine`.
- **Conséquences** : responsabilités isolées par agent ; `execution/` regroupe transformations et exécution (coordination requise).

## ADR-002 — Interfaces = `Protocol` + `dataclass(frozen=True)`

- **Date** : 2026-10-15 — **Statut** : accepté.
- **Décision** : les ports remplaçables sont des `typing.Protocol` ; les objets de valeur sont des `dataclass` gelées ; `typing` seul, bibliothèque standard uniquement.
- **Conséquences** : immuabilité et provenance par construction ; pas de dépendance tierce.

## ADR-003 — Aucun moteur M3/Maude implémenté pour l'instant

- **Date** : 2026-10-15 — **Statut** : accepté.
- **Décision** : le dépôt ne livre que les interfaces ; `ReflectiveM3` est un `Protocol` dont les implémentations restent à fournir. Les `dataclass` n'implémentent pas la réflexion.
- **Conséquences** : aucune propriété formelle ne peut être revendiquée aujourd'hui.

## ADR-004 — Versionnage des langages M2

- **Date** : 2026-10-15 — **Statut** : accepté.
- **Décision** : `LanguageM2` porte `id` + `version` ; tout changement de définition exige un changement de `version`.
- **Conséquences** : reproductibilité et invalidation de cache fondées sur la version.

## ADR-005 — Harness de développement multi-agents

- **Date** : 2026-10-15 — **Statut** : accepté.
- **Décision** : orchestration par un agent `architect` (primary) déléguant à des sous-agents spécialisés, protocole DISCOVER → PLAN → DELEGATE → IMPLEMENT → VERIFY → REVIEW → INTEGRATE → RECORD (voir `docs/harness/PROTOCOL.md`).
- **Conséquences** : pas d'écritures concurrentes sur un même fichier ; parallélisme initial limité à 3.

## ADR-006 — Cache en trois couches (seul B est implémenté)

- **Date** : 2026-10-15 — **Statut** : accepté.
- **Décision** : couche A (contexte LLM, compaction native), couche B (cache de développement, `scripts/harness.py`), couche C (cache sémantique épistémologique, à concevoir). Voir `docs/harness/CACHE.md`.
- **Conséquences** : ne pas construire de framework de cache prématuré ; invalider dès qu'une dépendance est incertaine.

## ADR-007 — Taxonomie M2 partagée et expérience de transfert ARC

- **Date** : 2026-10-16 — **Statut** : implémenté expérimentalement et intégré par l'architecte.
- **Contexte** : les transformations globales atteignent 16/400 tâches de développement ARC. L'utilisateur demande un langage par tâche issu d'une taxonomie commune, et le transfert des découvertes entre langages.
- **Décision** : ajouter des composants internes dans `algorithms/`. Chaque M2 de tâche référence des versions immuables de familles partagées. Le DAG autorise l'héritage multiple ; les collisions de signatures/définitions sont rejetées. Les promotions produisent des définitions typées, une nouvelle version et une provenance source. Aucun export ni signature du contrat public ne change.
- **Sélection** : une méthode `LanguageDiscovery.fit` sépare la sélection sur train de la validation indépendante. L'ancien `discover` garde son sens exploratoire, explicitement documenté. ARC choisit un programme avant accès aux réponses test.
- **Transfert** : une composition cohérente sur au moins deux exemples peut devenir un opérateur réutilisable de sa famille. Son statut empirique reste candidat. Les descendants doivent choisir explicitement la nouvelle version. La définition n'est pas une généralisation empirique automatique.
- **Mesure** : comparer primitives globales, bibliothèque plate et recherche guidée par familles ; entraîner la mémoire sur `training`, la figer, puis mesurer sur `evaluation` sans adaptation à ses labels. Rapports par tâche, empreintes des données/code/mémoire, prédictions et liens aux validations conservés.
- **Conséquences et limites** : la taxonomie et la politique initiales sont manuelles. L'ablation teste un système de recherche, pas la seule topologie. Aucune preuve de généralité, ni boucle complète de révision des connaissances. `Grid` passe des exemples à `algorithms/grid_objects.py` avec réexport compatible ; les anciennes transformations deviennent des réexports de primitives partagées. Voir `TECHNICAL.md` et le rapport de mesure.

## ADR-008 — Apprenants ajustés à la tâche, séparés par rôle

- **Date** : 2026-10-16 — **Statut** : implémenté ; mesure de développement seulement.
- **Contexte** : les familles énumérées (ADR-007) ne couvrent pas les règles dont les paramètres dépendent de la tâche (assemblage de blocs, règle locale, recadrage).
- **Décision** : des apprenants purs `training -> (Grid -> Grid) | None` vivent dans `algorithms/`, par rôle et du plus bas au plus haut niveau : `grid_transforms`/`grid_objects` (primitives), `grid_features` (descripteurs de cellule sans tâche), `fitting` (types, `after`), `local_rule`, `layout_learners`, `extraction_learners`, `fitted_families` (registre famille → apprenants). `arc_language` ne déclare que les noms de familles ; le solveur n'importe que le registre. Aucun export ni signature publique ne change.
- **Sélection** : une fonction ajustée est vérifiée directement sur les paires d'entraînement sous la forme d'un terme `task_*(g)`, sans énumération, et n'est pas imputée à `max_candidates`. Les règles locales choisissent le descripteur à longueur de description minimale et exigent deux cellules de support par clé modifiée. Les opérateurs `task_*` ne sont jamais promus en mémoire.
- **Conséquences et limites** : un ajustement exact est un indice, pas une preuve de généralisation. Les descripteurs et familles sont manuels. La mémoire archivée de l'ADR-007 n'est plus importable. Le score 100/400 est une mesure de développement sur `training`, non indépendante.

## ADR-009 — Suppression des apprenants écrits en dur ; recherche compositionnelle

- **Date** : 2026-10-17 — **Statut** : implémenté ; remplace l'ADR-008.
- **Contexte** : les apprenants `task_*` (tuilage, partition, règle locale, extraction…) encodaient la structure des solutions en code humain. Le score qu'ils produisaient ne mesurait pas la découverte (règle critique d'`AGENTS.md`).
- **Décision** : `fitting`, `fitted_families`, `grid_features`, `local_rule`, `layout_learners`, `extraction_learners` sont supprimés, ainsi que les primitives `blank`, `block`, `assemble`, `crop_to_colors`, `dominant_color`. Ajout de primitives booléennes et spatiales petites (`logical_and/or/xor/not`, `hconcat`, `vconcat`, `dilate`, `erode`) et de nœuds de taxonomie `orientation`, `parts`, `logic`, `layout`. Seule estimation de paramètre conservée : une table de couleurs (`task_recolor`), via le crochet `complete`.
- **Recherche** : déduplication observationnelle sur la signature d'entraînement (indice, pas preuve) ; budgets `max_candidates` (total), `max_generated` (par famille), `max_nodes`.
- **Conséquences et limites** : le score baisse ; il décompose les tâches résolues par primitives composées. Les promotions faites dans `geometry` ne se propagent pas à `logic`/`layout`. Les anciens résultats (`*-fitted.json`, 100/400 et 48/400) viennent du code supprimé et ne sont pas reproductibles ; `scripts/audit_arc_results.py` et la mémoire archivée sont incompatibles.
