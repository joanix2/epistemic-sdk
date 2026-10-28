# Implémentation et expérience ARC

## Recherche et validation

`LanguageDiscovery.fit()` ne reçoit que les exemples d'entraînement. Il utilise `typed_search.enumerate_typed_terms()` : sortes exactes, ordre déterministe par taille. Avec une `signature`, les termes qui produisent les mêmes sorties d'entraînement sont dédupliqués (le plus petit est gardé, les équivalents observationnels sont masqués : indice, pas preuve d'équivalence). Un crochet `complete` accepte un candidat exactement ou après estimation sur l'entraînement d'une table de couleurs unique, enveloppée en `task_recolor(terme)`. Les plafonds de candidats résultats et de termes générés sont distincts. Un arrêt par budget ne signifie pas épuisement de l'espace.

L'ancien `LanguageDiscovery.discover()` reste une API exploratoire qui sélectionne avec une observation étiquetée ; il ne faut pas utiliser son résultat pour annoncer un score indépendant sur cette même observation. L'adaptateur ARC historique utilise maintenant `fit()`.

`TaxonomicSolver.solve(task_id, training)` ne reçoit aucune réponse cible. Le programme retenu est lié au `LanguageM2` matérialisé pour cette tâche. Le harness le convertit en `Hypothesis`/`ProgramM1`, l'exécute via `ProgramRunner`, puis utilise `ObservationValidator` pour produire les rapports de corroboration/réfutation. Les IDs d'observations train/test sont disjoints ; les validations et contre-exemples figurent dans les artefacts JSON.

## Taxonomie et objets

Les nouveaux composants sont internes à `epistemic_sdk/algorithms/` ; les 41 exports publics restent inchangés.

- `grid_objects.py` : `Grid`, composantes connexes, objets, sélection, extraction, nettoyage, trous, symétries. L'arrière-plan et la connexité sont des hypothèses explicites. `examples.arc.loader.Grid` réexporte la même classe ; les grilles non rectangulaires sont rejetées.
- `grid_transforms.py` : primitives globales partagées ; l'ancien module d'exemple les réexporte.
- `language_taxonomy.py` : DAG append-only, références `(node_id, version)`, parents figés, contrôle des signatures et définitions, héritage multiple, instantanés et sérialisation. Les versions internes sont des entiers textuels. Les callables primitifs restent des sémantiques de confiance.
- `arc_language.py` : familles initiales `geometry`, `objects`, `object_selection`, `symmetry`, `topology`, `dynamics`, `object_geometry`, `orientation`, `parts`, `logic` (et/ou/xor/non), `layout` (hconcat/vconcat). Aucune famille ajustée : les apprenants `task_*` ont été supprimés (ADR-009). Le graphe et ses primitives sont spécifiés manuellement.
- Seule estimation sur l'entraînement autorisée : une constante (table de recoloration), via `task_recolor`. Les fonctions complexes (tuilage, partition, règle locale, extraction) ne sont pas écrites en dur : elles doivent être des compositions de primitives retrouvées par recherche.
- `taxonomic_solver.py` : sélection de familles à partir de l'entraînement, spécialisation par tâche, interprétation mémorisée localement, apprentissage et sauvegarde de définitions. Les familles sont explorées dans l'ordre choisi avec le budget global `max_candidates` et un plafond `max_generated` de termes générés par famille. `task_recolor` n'est jamais promu en mémoire.

## Mémoire et transfert

`learn()` retient des compositions cohérentes avec au moins deux exemples d'une tâche source, sans lire ses réponses de test. La définition est typée et attachée à la famille où elle a été découverte. Son statut empirique reste `candidate` : une définition exacte n'est pas une preuve que la règle s'applique à toutes les tâches.

Une promotion crée une version ; les anciens programmes gardent leurs parents. `object_geometry` est explicitement recréé pour hériter des nouvelles définitions de ses parents. Chaque tâche cible vérifie les opérateurs hérités sur son propre entraînement avant de les appliquer. Les définitions apprises sont développées dans le même évaluateur que les expressions initiales, avec les mêmes contrôles de taille intermédiaire.

La mémoire JSON exclut les spécialisations et callbacks ajustés à une tâche. L'import exige le même ensemble de primitives initiales ; il ne certifie pas l'identité de leur code. L'évaluation ne modifie pas la mémoire réutilisable. Le rapport source et le fichier mémoire doivent être archivés ensemble, avec les rapports cibles dont l'empreinte de mémoire concorde.

## Reproduction

Les commandes utilisent le dossier ARC-AGI-1 public. Remplacer les chemins si nécessaire.

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/ruff check .
.venv/bin/mypy epistemic_sdk examples tests
.venv/bin/python scripts/harness.py check

# Développement : global, flat ou taxonomy ; sélection indépendante des labels test.
.venv/bin/python -m examples.arc.transfer_measure --mode taxonomy \
  --data-dir /home/joan/Documents/Programation/ARC-AGI/data/training \
  --output /tmp/arc-training-taxonomy.json

# Apprentissage sur training, puis mémoire figée sur evaluation.
.venv/bin/python -m examples.arc.transfer_measure --mode transfer \
  --source-dir /home/joan/Documents/Programation/ARC-AGI/data/training \
  --data-dir /home/joan/Documents/Programation/ARC-AGI/data/evaluation \
  --memory-out /tmp/arc-memory.json --output /tmp/arc-transfer.json

# Ablation : exactement les mêmes définitions dans un langage plat.
.venv/bin/python -m examples.arc.transfer_measure --mode flat-memory \
  --memory-in /tmp/arc-memory.json --output /tmp/arc-flat-memory.json
```

Les scores utilisent une seule prédiction sélectionnée par entrée et exigent tous les exemples test corrects pour compter une tâche. Ce ne sont pas des scores privés/officiels ARC Prize. Une comparaison flat/taxonomy mesure aussi l'ordre de recherche et les sous-espaces admissibles ; elle n'isole pas causalement la seule topologie. Le budget de candidats résultats n'est pas une égalité de coût machine.

## Limites restantes

La recherche reste bornée et déterministe, le choix de famille est heuristique, les types ne comprennent pas de coercions de subsorts, et la promotion n'apprend pas une taxonomie générale. La boucle complète de révision des croyances/connaissances n'est pas intégrée à ce solveur. Les défauts précédemment relevés dans l'e-graph, les moteurs ILP/ASP et les exemples de révision booléenne restent hors de cette modification ; le nouveau chemin ARC ne les utilise pas.
