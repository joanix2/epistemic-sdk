# ARC : objets, taxonomie et transfert — 2026-10-16

L'architecture augmente la couverture sur les deux ensembles publics : **16 → 26 tâches de développement** et **1 → 4 tâches d'évaluation**. Le transfert de définitions fonctionne, mais son gain dépend de la recherche : il ajoute une tâche au contrôle plat, aucune à la recherche par taxonomie.

## Protocole

- ARC-AGI-1 public, dépôt de données au commit `399030444e0ab0cc8b4e199870fb20b863846f34` : 400 tâches `training`, 400 tâches `evaluation`, identifiants disjoints.
- Une seule prédiction choisie par entrée test ; tous les exemples test d'une tâche doivent être exacts. Les réponses test n'interviennent jamais dans le choix du programme, du langage ni dans l'apprentissage de mémoire.
- Développement sur `training`. La mémoire utilise uniquement les démonstrations `train` des tâches source, en ordre lexicographique. Huit définitions sont retenues, avec statut empirique `candidate`, scope, version et références des observations source.
- Le code de recherche est figé avant l'évaluation cible. La mémoire est figée et son empreinte est contrôlée après chaque balayage. Le contrôle `flat-memory` importe exactement la mémoire de `transfer`.
- Les programmes passent par `Hypothesis`/`ProgramM1`, `ProgramRunner` et `ObservationValidator`. Les JSON contiennent les prédictions et liens vers validations/contre-exemples. Les réponses cibles sont consultées seulement après sélection.
- Il s'agit de mesures locales sur des données publiques, **pas d'un score officiel privé ARC Prize**, et pas d'ARC-AGI-2.

## Résultats

| Système | Développement, 400 tâches | Évaluation, 400 tâches |
|---|---:|---:|
| Transformations globales, référence corrigée sans sélection sur test | 16 (4 %) | 1 (0,25 %) |
| Bibliothèque plate avec les nouvelles primitives | 20 (5 %) | 2 (0,5 %) |
| Recherche par taxonomie, sans mémoire apprise | **26 (6,5 %)** | **4 (1 %)** |
| Bibliothèque plate + mémoire source figée | non mesuré | 3 (0,75 %) |
| Taxonomie + même mémoire source figée | non mesuré | **4 (1 %)** |

Sur le développement, la taxonomie résout 16 tâches par la famille géométrique, six par la sélection d'objets, deux par la topologie et deux par la symétrie. Le gain face à la référence est de dix tâches, soit +2,5 points et +62,5 % en nombre de tâches. Sur l'évaluation, le gain absolu est de trois tâches ; le niveau reste faible.

La différence plat/taxonomie mesure un **système de recherche guidé par familles**. L'ordre de recherche, les compositions autorisées et les limites de taille diffèrent ; elle ne démontre pas un effet causal isolé de la topologie du DAG.

## Transfert observé et résultat négatif

La définition `learned_66758ca1b319`, découverte sur la tâche source `1f85a75f`, compose segmentation des composantes de premier plan, sélection du plus grand objet et extraction. Elle est réutilisée avec succès sur `cd3c21df`, sans réapprendre la composition. Les labels test de la source n'ont pas servi à l'admission de cette définition.

| Comparaison sur `cd3c21df` | Sans mémoire | Avec mémoire |
|---|---:|---:|
| Recherche par taxonomie | résolue, 207 candidats | résolue, 190 candidats |
| Recherche plate | échec au plafond de 5 000 candidats | résolue, 9 candidats |

Le contrôle plat gagne donc cette tâche et n'en perd aucune. La taxonomie ne gagne ni ne perd de tâche avec mémoire. Sur l'ensemble d'évaluation, la mémoire augmente légèrement le total des candidats de la taxonomie : **1 980 511 → 1 980 854**. Le nombre de réutilisations ne constitue pas, à lui seul, une preuve de gain global.

Les plafonds sont de 5 000 candidats résultats par tâche et 50 000 termes générés par recherche de famille. Les familles géométrie/symétrie/topologie sont explorées jusqu'à trois nœuds, objets/composition et le contrôle plat jusqu'à cinq. La référence globale est limitée à trois nœuds. Les macros comptent comme opérations dans la recherche, mais leurs expressions sont développées à l'exécution et subissent les mêmes limites intermédiaires de taille.

Les durées mesurées sont environ 51 s pour la taxonomie sans mémoire et 166 s avec mémoire, contre 56 s / 169 s pour les contrôles plats. Les processus ont partiellement tourné en parallèle : ce ne sont pas des comparaisons de temps machine isolées. Aucun gain global de vitesse n'est revendiqué ; l'ajout de macros élargit aussi l'espace de recherche.

## Ce que l'expérience éprouve

- M2 de tâche rattaché à des versions de familles partagées, et non créé isolément.
- Objets et collections d'objets comme sortes intermédiaires ; recherche respectant les signatures.
- Héritage multiple, contrôle de collisions, promotion explicite, maintien des anciennes versions.
- Définition apprise sérialisée, réimportée et exécutée sur une autre tâche ; héritage par une famille composée testé.
- Sélection indépendante des réponses test et validations traçables.

La taxonomie et les primitives initiales sont construites manuellement. La règle d'admission « composition cohérente sur au moins deux démonstrations » est une heuristique ; elle n'établit pas la généralité empirique d'un principe. Le choix automatique d'une taxonomie, les traductions entre représentations et la boucle complète de réfutation/révision de connaissances restent ouverts. Le solveur n'utilise pas les composants historiques e-graph/ILP/ASP/révision booléenne dont l'audit a relevé des défauts.

Deux défauts ont été corrigés lors de la revue avant les mesures finales : contournement des limites intermédiaires par les macros et absence de plafond sur la génération des sous-termes. Ils disposent de tests de régression. Le test historique de réflexion a reçu un second exemple d'entraînement pour distinguer la réflexion d'un recoloriage également compatible avec son unique démonstration.

## Apprenants ajustés à la tâche (développement uniquement)

Après la mesure ci-dessus, quatre familles ont été ajoutées à la taxonomie : `tiling`, `partition`, `extraction` et `local_rule`. Chacune regroupe des apprenants qui estiment leurs paramètres sur les exemples d'entraînement d'une tâche (assemblage de blocs, fractale, expansion de cellule, combinaison de parties, réduction de blocs, recadrage par couleur, résumé de couleur, fenêtre, règle locale sur descripteur de cellule). Chacun est aussi essayé après recadrage sur la boîte englobante (`*_cropped`).

| Mesure `training`, mode taxonomie | Tâches résolues |
|---|---:|
| Avant (section Résultats) | 26 (6,5 %) |
| Avec apprenants ajustés | **100 (25 %)** |

Mesure sur `evaluation`, lancée une seule fois avec ce code (mode taxonomie, sans mémoire) : **48/400 (12 %)**, archivée dans [evaluation-taxonomy-fitted.json](evaluation-taxonomy-fitted.json). C'est la meilleure estimation locale de généralisation ; l'écart avec les 25 % de `training` reflète le réglage sur ce jeu. Après cette lecture, `evaluation` n'est plus réservé : toute optimisation suivante guidée par lui exige un nouveau protocole.

Par famille : règle locale 33, géométrie 20, tiling 15, partition 13, sélection d'objets 7, extraction 5, dynamique 3, topologie 2, symétrie 2. Résultat archivé : [training-taxonomy-fitted.json](training-taxonomy-fitted.json). Commande : `transfer_measure --mode taxonomy` sur `training`, avec `max_candidates=5000`.

Précautions d'interprétation :

- Mesure de développement uniquement : le code a été réglé en lisant les échecs de `training`. Ce n'est ni une validation indépendante ni un score ARC Prize. Les 4/400 d'évaluation de la section précédente décrivent l'ancienne architecture ; la mesure avec ce code est 48/400 (ci-dessus).
- Un apprenant qui reproduit tous les exemples d'entraînement est un indice d'ajustement, pas une preuve de généralisation. Les règles locales exigent deux cellules de support par clé modifiée et choisissent le descripteur à longueur de description minimale ; les clés inconnues laissent la cellule inchangée, hypothèse vérifiée uniquement sur l'entraînement.
- Les descripteurs, primitives et familles sont écrits à la main. Le gain mesure aussi cette expertise, pas la découverte autonome du langage.
- Les apprenants sont vérifiés directement sur l'entraînement et ne comptent pas dans `max_candidates` ; les scores `candidates` ne sont donc pas comparables avec la section précédente. En mode plat, ils sont de simples opérateurs de la recherche énumérative.
- `memory.json` et `evaluation-*.json` ne sont pas régénérés : la mémoire archivée n'est plus importable (familles et primitives modifiées) et `scripts/audit_arc_results.py` échoue volontairement car il exige la source figée de la première mesure.

## Artefacts et audit

- [Comparaisons détaillées](comparison.json) : scores, coûts, tâches gagnées/perdues, réutilisations.
- [Mémoire partagée](memory.json) : huit définitions et leur provenance.
- [Évaluation globale](evaluation-global.json), [plate](evaluation-flat.json), [taxonomie](evaluation-taxonomy.json), [plate avec mémoire](evaluation-flat-memory.json), [taxonomie avec mémoire](evaluation-transfer.json).
- [Développement global](training-global.json), [plat](training-flat.json), [taxonomie](training-taxonomy.json).
- [Empreintes du code](source-audit.json). Tous les balayages ont utilisé la même empreinte source `6b3682cabbb4…`. Après leur fin, seule une ligne vide finale a été supprimée dans un réexport ; l'égalité des empreintes AST avant/après est consignée. Les empreintes exécutées originales sont conservées dans les rapports.

Les rapports `transfer` et `flat-memory` ont la même empreinte de mémoire `c2560fd68737…`. L'empreinte du jeu source figure dans `evaluation-transfer.json` ; le rapport de réimport ne la redéclare pas et doit être conservé avec ce rapport source et le fichier mémoire.

Audit reproductible des prédictions archivées, des métriques, des empreintes et des liens de validation :

```bash
.venv/bin/python scripts/audit_arc_results.py
```

Au moment de la première mesure, les 150 tests passaient, ainsi que Ruff, mypy et le harness de contrats (41 exports inchangés) ; ils passent aussi avec les apprenants (180 tests). Les commandes complètes de reproduction se trouvent dans [TECHNICAL.md](../../../TECHNICAL.md).

Pour poursuivre, régler l'admission et la priorité des abstractions sur des partitions du développement. Une optimisation désormais pilotée par les résultats de ce dossier `evaluation` nécessitera un nouveau protocole réservé pour revendiquer une validation indépendante.
