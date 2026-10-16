# PROGRESS — expérience de transfert ARC (2026-10-16)

## Mise à jour : apprenants ajustés à la tâche (développement uniquement)

- La recherche par taxonomie atteint **100/400** sur `training` (contre 26/400 ci-dessous) et **48/400 (12 %) sur `evaluation`**, lancé une fois (contre 4/400 avant) ; l'évaluation n'est plus réservée, mesure locale d'une seule prédiction par entrée, sans score officiel ARC Prize. Détail par famille et limites : `docs/experiments/arc-taxonomy/REPORT.md` (section « Apprenants ajustés à la tâche »).
- Nouvelles familles `tiling`, `partition`, `extraction`, `local_rule`, chacune avec une variante `*_cropped`. Leurs paramètres sont estimés sur les exemples d'entraînement par des apprenants (`fitting`, `layout_learners`, `extraction_learners`, `local_rule`, descripteurs de cellule dans `grid_features`). Ils sont vérifiés directement et non énumérés ; leur coût n'est pas imputé au budget `max_candidates`.
- Les anciens chiffres d'évaluation (4/400) et la mémoire archivée `memory.json` correspondent à l'architecture précédente : la mémoire n'est plus importable (familles et primitives modifiées) et ne sont pas comparables au nouveau code.
- 180 tests, Ruff, mypy (143 fichiers) et harness check passent ; 41 exports publics inchangés.

## État précédent (26/400)

- Architecture intégrée : objets typés, taxonomie de familles M2, spécialisations par tâche, mémoire de définitions avec versions et provenance.
- Sélection des programmes sur les seuls exemples d'entraînement. Les réponses test sont réservées à la validation.
- Développement ARC-AGI-1 : global **16/400**, bibliothèque plate **20/400**, recherche par taxonomie **26/400**.
- Évaluation publique séparée : global **1/400**, bibliothèque plate **2/400**, taxonomie **4/400**. Ce ne sont pas des scores privés ARC Prize.
- Mémoire : **8 définitions** apprises sur les démonstrations source ; figées avant l'évaluation. Avec transfert : **4/400**, une réutilisation réussie, aucun gain ni perte de tâche face à la taxonomie sans mémoire. Sur cette tâche : 207 → 190 candidats, mais 1 980 511 → 1 980 854 candidats au total.
- Contrôle avec exactement la même mémoire : le langage plat passe de **2/400 à 3/400** ; la tâche supplémentaire passe de l'échec à 5 000 candidats à une solution en neuf candidats. La mémoire permet donc un transfert sous budget, sans améliorer le score de la taxonomie dans cette expérience.
- **150 tests**, Ruff, mypy (132 fichiers) et harness check passent ; 41 exports publics inchangés. Aucun commit créé. Les fichiers non suivis préexistants ont été conservés.
- Rapport détaillé et ablations : `docs/experiments/arc-taxonomy/REPORT.md`. Commandes et limites : `TECHNICAL.md`.

## Ce qui est établi et ce qui reste ouvert

Le nouveau langage d'objets et la sélection par familles améliorent la couverture sur les deux ensembles. L'héritage et la réutilisation de définitions sont exécutables et testés. L'effet du transfert sur le score global n'est pas établi ; sa politique actuelle augmente légèrement la recherche totale. Le gain flat/taxonomy inclut la politique de recherche et les compositions autorisées, pas seulement la topologie du graphe.

La taxonomie initiale et la segmentation des objets restent des choix manuels. Ni la découverte autonome d'une taxonomie, ni la généralisation universelle d'un principe, ni la boucle complète de révision des connaissances ne sont démontrées. Ne plus présenter les quatre problèmes scientifiques comme entièrement validés.

## Suites possibles

- Apprendre les priorités de familles et l'admission des abstractions sur des partitions du développement ; mesurer le coût des définitions peu utiles.
- Concevoir des relations de transfert avec conditions d'applicabilité et traductions entre représentations.
- Intégrer la réfutation et l'invalidation traçable, puis traiter les défauts historiques relevés par l'audit.
- Toute nouvelle optimisation fondée sur les résultats `evaluation` rend cet ensemble impropre à une nouvelle revendication de validation indépendante ; utiliser un autre protocole réservé.

## Historique antérieur (conservé, certaines assertions sont dépassées)

# PROGRESS — reprise du travail de nuit

## État (dernier commit)

- Branche `arc-prize`, arbre propre. 4 problèmes du SDK **validés** (booléen + flou).
- `ruff` / `mypy` / `unittest` verts (`uv run python -m unittest discover -s tests`).

## Fait (ARC)

- `examples/arc/loader.py` — `Grid` (immutable, hashable), `Example`, `Task`, `load_task`, `load_training_tasks`.
- `examples/arc/transformations.py` — `recolor`, `flip_horizontal`, `flip_vertical`, `discover_recolor` **+** `rotate_90/180/270`, `transpose`, `anti_transpose` (symétrie diagonale), `crop` (boîte englobante des cellules non-nulles), `upscale(factor)` (agrandissement entier), `pad_square` (complétion en carré).
- `examples/arc/discovery.py` — adaptateur réutilisant la boucle **`LanguageDiscovery` du SDK** : `transformation_language()` construit un `LanguageM2` (`arc_grid` v1.0.0, opérateurs unaires `Grid→Grid`), `discover_task(task)` énumère les compositions (≤ 3 nœuds) et valide sur `task.test`, `OPERATOR_FAMILY` classe chaque solution par famille (`recolor`, `flip`, `rotation`, `diagonal`, `crop`, `scale`, `padding`, `composition`, `identity`).
  - Décision : `PROBE_GRIDS` ajoutées au domaine d'équivalence sémantique pour éviter que deux opérateurs distincts (ex. `recolor` vs `flip_horizontal`) ne soient fusionnés lorsqu'il n'y a qu'un seul exemple d'entraînement. Les sondes n'affectent que la déduplication, pas la cohérence → pas de fuite entraînement/test.
- Résultat **mesuré** : 16/400 tâches résolues (`max_nodes=3`, ~2 s ; `max_nodes=4` identique mais ~34 s — les compositions de profondeur 2 suffisent). Répartition par famille primaire : recolor 4, rotation 3, flip 2, diagonal 2, scale 2, composition 2, crop 1.
- Analyse du plafond : relations de dimensions entrée/sortie sur les 400 tâches (entraînement) — **262 mêmes dimensions**, 100 réduites (crop), 15 agrandies (pad/scale), 11 `scale2`, 5 `scale3`, 7 variables. La majorité des tâches « mêmes dimensions » ne sont **pas** des transformations globales simples (manipulation d'objets, recoloriage conditionnel) : le plafond des transformations globales est structurellement bas.
- Données ARC clonées dans `/home/joan/Documents/Programation/ARC-AGI` (configurable via `ARC_DATA_DIR`).

## Mesure (harness)

`examples/arc/measure.py` balaie les 400 tâches et agrège par famille (`--limit`, `--json` disponibles). `tests/test_arc_measure.py` couvre les cas synthétiques + un échantillon réel.

```
python -m examples.arc.measure
solved 16/400 (4.0%)
by family:
  composition: 2 (0.5%)   crop: 1 (0.2%)   diagonal: 2 (0.5%)   flip: 2 (0.5%)
  recolor: 4 (1.0%)       rotation: 3 (0.8%)   scale: 2 (0.5%)
participation: crop 3, diagonal 2, flip 3, recolor 4, rotation 3, scale 3
```

## Plafond des transformations globales (résultat négatif documenté)

Une bibliothèque élargie de transformations **unaires** évaluée seule (train+test) plafonne à une **union de 15 tâches** — moins que les 16 obtenues par compositions : `rot180` 2, `transpose` 2, `mirror_h` 2, `mirror_v` 2, `rot270/flip_h/flip_v/crop_bbox/gravity_down/upscale2/upscale3` 1 chacun. Les opérateurs paramétrés testés (`crop_color{c}`, `keep_color{c}`, `remove_color{c}`, `replace_bg{c}`, `downscale{2,3}`, `outline`) n'ajoutent **aucune** tâche.

Conclusion : l'espace des transformations globales est épuisé autour de ~4 %. Progresser exige le **raisonnement au niveau objet** (sélection d'objet, complétion de symétrie, règles conditionnées par la couleur/forme) — un changement de langage M2, pas un ajout d'opérateur.

## Prochaines étapes (objectif de nuit)

1. **Augmenter la couverture** : transformations paramétrées (facteur variable, recoloriage conditionnel), sélection d'objet / crop vers une couleur cible. Mesurer après chaque ajout ; documenter les échecs (règle des 3 échecs).
2. **Documenter le plafond** : les transformations globales ne couvrent qu'une faible fraction d'ARC (~4 %) ; l'étape suivante est le raisonnement au niveau objet (sélection, gravité, complétion de symétrie), hors du périmètre « transformations globales » actuel.

## Garde-fous

- `ruff` + `mypy` + `unittest` verts avant chaque commit.
- Ne pas modifier les interfaces publiques (`epistemic_sdk/__init__.py`, `__all__`) sans justification.
- Pas de dépendance tierce sans justification (règle AGENTS.md).
- Documenter les blocages ici ; passer à la tâche suivante après 3 échecs documentés.
