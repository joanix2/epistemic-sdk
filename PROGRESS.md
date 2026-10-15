# PROGRESS — reprise du travail de nuit

## État (dernier commit)

- Branche `arc-prize`, arbre propre. 4 problèmes du SDK **validés** (booléen + flou).
- `ruff` / `mypy` / `unittest` verts (`uv run python -m unittest discover -s tests`).

## Fait (ARC)

- `examples/arc/loader.py` — `Grid` (immutable, hashable), `Example`, `Task`, `load_task`, `load_training_tasks`.
- `examples/arc/transformations.py` — `recolor`, `flip_horizontal`, `flip_vertical`, `discover_recolor`.
- Résultat : `discover_recolor` résout **4/400** tâches d'entraînement ARC (recolor pur). Exemples : `0d3d703e`, `b1948b0a`, `c8f0f002`, `d511f180`.
- Données ARC clonées dans `/home/joan/Documents/Programation/ARC-AGI` (configurable via `ARC_DATA_DIR`).

## Prochaines étapes (objectif de nuit)

1. **Plus de transformations** : crop (rognage), scale (agrandissement), padding, symétrie diagonale, rotation — et une fonction `discover` qui essaie chacune et valide sur `task.test`.
2. **Un « langage » de transformations** : composer les transformations (séquences) comme des programmes M1, pour réutiliser la boucle synthèse/validation/révision du SDK au lieu d'une énumération ad hoc.
3. **Mesurer** : taux de résolution sur les 400 tâches d'entraînement, par famille de transformation.

## Garde-fous

- `ruff` + `mypy` + `unittest` verts avant chaque commit.
- Ne pas modifier les interfaces publiques (`epistemic_sdk/__init__.py`, `__all__`) sans justification.
- Pas de dépendance tierce sans justification (règle AGENTS.md).
- Documenter les blocages ici ; passer à la tâche suivante après 3 échecs documentés.
