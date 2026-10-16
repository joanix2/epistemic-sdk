# État de reprise

## Travail intégré

Expérience ARC de taxonomie et transfert (ADR-007), réalisée le 2026-10-16. Modules internes de grilles/objets, recherche typée, taxonomie versionnée et définitions persistantes. `LanguageDiscovery.fit` sépare sélection et test. Aucun export public modifié, aucune dépendance ajoutée, aucun commit.

## Résultats confirmés

- 180 tests réussis ; Ruff et mypy sur SDK/exemples/tests passent ; harness check vérifie les 41 exports.
- ARC-AGI-1 training : 16/400 global, 20/400 plat, 26/400 taxonomie, puis **100/400** taxonomie avec apprenants ajustés à la tâche (développement ; evaluation non relancée avec ce code).
- ARC-AGI-1 evaluation : 1/400 global, 2/400 plat, 4/400 taxonomie, 4/400 avec mémoire source figée.
- Huit définitions source ; une réutilisation cible réussie, sans gain de couverture. Le coût total en candidats augmente légèrement. Pas de score officiel privé ARC Prize.

## Limites / reprise

`TECHNICAL.md` décrit les APIs internes et les commandes. `docs/experiments/arc-taxonomy/REPORT.md` et les JSON sont la source des mesures, des empreintes et des limites d'interprétation. Le graphe et la politique initiaux sont manuels. L'ancien `discover` utilise son observation étiquetée pour la sélection ; employer `fit` pour une mesure indépendante.

Les défauts e-graph, ILP/ASP et révision booléenne de l'audit restent hors périmètre et hors du nouveau chemin ARC. Aucun moteur réflexif Maude ni cache épistémique général n'est implémenté. La boucle complète de révision reste à intégrer.
