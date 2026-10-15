# Cache et invalidation

Trois couches distinctes. Seule la couche B est implémentée aujourd'hui.

## A. Cache de contexte LLM

- Instructions système stables ; contexte commun (AGENTS.md) avant le contexte spécifique.
- Chargement progressif des documents (à la demande), jamais tout le dépôt.
- Réutiliser les rapports structurés au lieu de réinjecter les conversations.
- Compaction native d'OpenCode activée (`opencode.json` → `compaction.auto: true`).
- **Ne pas supposer** un cache de prompts fournisseur accessible : vérifier les capacités du fournisseur avant de les exploiter. Aucun hook non standard n'est requis.

## B. Cache de développement (implémenté)

`scripts/harness.py run` calcule une empreinte avant d'exécuter les tests :

- Fichiers sources pertinents (`epistemic_sdk/`, `examples/`, `tests/`).
- Configuration (`pyproject.toml`).
- Version de Python et entrées du test.

Règles :

- Si l'empreinte est inchangée et la dernière exécution a réussi, on réutilise le résultat.
- `--no-cache` force la ré-exécution.
- Si une dépendance ne peut être déterminée de façon sûre, **relancer les tests**.
- Le cache stocké est un JSON dans `.cache/` (ignoré par Git) ; il n'invalide jamais seul une décision humaine.

## C. Cache sémantique épistémologique (à concevoir)

Cible : normalisation de programmes, transformations déterministes, exécutions reproductibles, recherche d'équivalence syntaxique, validations réutilisables **sous conditions strictes**.

Clé d'invalidation complète (tout ce qui influence le résultat) :

- Identité **et contenu** du programme.
- Version et définition complète du `LanguageM2`.
- Axiomes et règles pertinents.
- Version du moteur M3.
- Versions et ordre des transformations.
- Contexte d'exécution.
- Entrées et observations utilisées.
- Version du validateur.
- Configuration, environnement, graine aléatoire (si applicable).

Règles d'invalidation :

- Une nouvelle observation ou un axiome modifié **invalide** les résultats dépendants.
- Ne **jamais** réutiliser une corroboration sur la seule identité d'une hypothèse.
- Ne **pas** mettre en cache par défaut les exécutions non déterministes ou à effets externes.

## État

- Couche A : configurée (compaction native).
- Couche B : implémentée dans `scripts/harness.py`.
- Couche C : **conception documentée seulement**, aucune implémentation.
