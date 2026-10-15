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
