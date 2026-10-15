# Protocole du harness de développement

Processus en huit phases : **DISCOVER → PLAN → DELEGATE → IMPLEMENT → VERIFY → REVIEW → INTEGRATE → RECORD**.

## Phases

1. **DISCOVER** — lire `AGENTS.md`, `docs/architecture/OVERVIEW.md` et `DEPENDENCIES.md`, `git status`/`diff`/`log` ; identifier les modules impactés. Ne pas relire tout le dépôt.
2. **PLAN** — construire le graphe de dépendances des tâches ; découper en unités indépendantes ; définir les contrats.
3. **DELEGATE** — émettre un contrat (ci-dessous) à un sous-agent spécialisé ; en parallèle uniquement pour les tâches indépendantes (max 3) ; jamais d'écritures concurrentes sur un même fichier.
4. **IMPLEMENT** — le sous-agent implémente dans son périmètre.
5. **VERIFY** — tests locaux du sous-agent, puis validation d'intégration par l'architecte (`python -m unittest discover -s tests -v`, `python scripts/harness.py check`).
6. **REVIEW** — revue contradictoire (`epistemic-critic`) pour les changements à haut risque.
7. **INTEGRATE** — l'architecte fusionne, contrôle les changements inter-modules, met à jour `DECISIONS.md` et `STATE.md`.
8. **RECORD** — consigner le rapport structuré et les résultats confirmés.

## Contrat de tâche

Chaque délégation précise :

- **Task ID** — identifiant unique.
- **Objectif** — but mesurable.
- **Périmètre de fichiers autorisés** — chemins exacts (aucun module non concerné).
- **Interfaces concernées** — signatures publiques touchées ou à respecter.
- **Invariants à préserver** — référence aux invariants d'`AGENTS.md`.
- **Critères d'acceptation** — conditions vérifiables de réussite.
- **Tests à exécuter** — commandes exactes.
- **Dépendances à consulter** — documents/modules à lire.
- **Budget indicatif** — contexte et nombre d'itérations.

## Rapport structuré (retour de sous-agent)

Le sous-agent retourne, sans que l'architecte ait à relire sa conversation :

- **Modifications réalisées** — fichiers et résumé.
- **Interfaces affectées** — signatures modifiées ou ajoutées.
- **Tests exécutés et résultats** — commandes et sorties.
- **Propriétés vérifiées** — et, surtout, les **non-preuves**.
- **Incertitudes et limites**.
- **Risques de régression**.
- **Décisions nécessaires** — points à trancher par l'architecte.

## Points de contrôle

- Après DELEGATE : le contrat est complet et non ambigu.
- Après IMPLEMENT : les tests locaux passent.
- Après VERIFY : la suite d'intégration passe.
- Après REVIEW : les failles signalées sont traitées ou explicitement acceptées.
- Une tâche en échec **n'est jamais** marquée terminée.

## Règles d'économie

- Ne pas déléguer une tâche triviale.
- Ne pas invoquer de « réunions » entre agents ; un seul échange contrat → rapport.
- Pas de résumés récursifs ; réutiliser les conclusions déjà validées.
- Coût d'orchestration < coût de la tâche.
