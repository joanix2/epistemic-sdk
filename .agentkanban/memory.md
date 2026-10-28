# Contexte persistant

- Direction retenue : un M2 par tâche, spécialisé depuis une taxonomie partagée ; transférer les définitions et conserver leur portée/provenance. Aucun langage jetable isolé et aucune assimilation d'une définition à une vérité empirique générale.
- Les nouveaux algorithmes ARC sont internes à `epistemic_sdk/algorithms/`. Les 41 exports publics sont inchangés.
- `LanguageDiscovery.fit` effectue la sélection sans labels test ; l'ancien `discover` reste exploratoire et ne fournit pas une mesure indépendante de sa propre observation de sélection.
- Expérience du 2026-10-16 : objets + taxonomie, mémoire apprise sur les seuls exemples `train` des tâches source, puis figée sur les tâches cibles. Source officielle locale : ARC-AGI-1 public, 400 training et 400 evaluation ; aucun score privé ARC Prize.
- Référence technique : `TECHNICAL.md`, ADR-007, `docs/experiments/arc-taxonomy/REPORT.md`. Les artefacts détaillent les prédictions, validations, versions et empreintes.
- La révision booléenne historique, les défauts ILP/ASP et e-graph signalés par l'audit restent hors du chemin ARC actuel. Le transfert de macros ne démontre ni une taxonomie apprise ni toute la boucle de révision.
