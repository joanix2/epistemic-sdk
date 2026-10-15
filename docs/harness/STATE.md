# État de reprise (STATE)

Mémoire de reprise, pas un second historique Git. N'y consigner que les faits utiles pour reprendre le travail.

## Travaux en cours

- Mise en place de l'infrastructure multi-agents (AGENTS.md, opencode.json, agents, docs, harness) — en cours, non validée par l'architecte.

## Derniers résultats confirmés

- `python -m unittest discover -s tests -v` : 3 tests de contrats passent.
- Le dépôt ne contient que les interfaces ; aucun moteur (Maude, synthèse, solveurs) n'est implémenté.
- Exemple M2/M1 : `examples/nat_language.py` (langage `nat` v1.0.0) charge et s'affiche.

## Prochains objectifs

1. Valider l'infrastructure multi-agents (restart OpenCode, charger `@architect`).
2. Cas d'étude fondateur : algèbre booléenne M2 (constantes, NOT, AND, OR, lois) + découverte de programmes M1.
3. Implémenter les instances d'algorithmes (génétique, EBM, ILP, MLP, Z3) derrière `InferenceEngine`/`Executor`.
4. Monter les niveaux de validation 3→7 (M3, M2, M1, validation, boucle de bout en bout).
5. Concevoir le cache sémantique (couche C).

## Blocages identifiés

- Aucun blocage technique. La conception du cache sémantique (couche C) reste ouverte.
- `pyproject.toml` référence encore `epistemic.__main__` alors que le paquet s'appelle `epistemic_sdk` (incohérence à traiter lors du premier travail d'intégration).
