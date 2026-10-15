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

## Prochaines étapes (objectif de nuit)

1. **Augmenter la couverture** : transformations paramétrées (facteur variable, recoloriage conditionnel), sélection d'objet / crop vers une couleur cible. Mesurer après chaque ajout ; documenter les échecs (règle des 3 échecs).
2. **Documenter le plafond** : les transformations globales ne couvrent qu'une faible fraction d'ARC (~4 %) ; l'étape suivante est le raisonnement au niveau objet (sélection, gravité, complétion de symétrie), hors du périmètre « transformations globales » actuel.

## Garde-fous

- `ruff` + `mypy` + `unittest` verts avant chaque commit.
- Ne pas modifier les interfaces publiques (`epistemic_sdk/__init__.py`, `__all__`) sans justification.
- Pas de dépendance tierce sans justification (règle AGENTS.md).
- Documenter les blocages ici ; passer à la tâche suivante après 3 échecs documentés.
