# Epistemic SDK — prototype exécutable 0.1

Un noyau d'interfaces épistémologiques, avec une implémentation de référence sur des domaines finis. Python 3.10+, bibliothèque standard uniquement. Aucun service externe, LLM ou clé API nécessaire.

## Lancer

Depuis le dossier extrait :

```bash
python -m epistemic
python -m epistemic --task examples/xor_grid.json --output runs
python -m unittest discover -s tests -v
```

L'installation est facultative (`pip install -e .`). La commande `epistemic-demo` devient alors disponible.

## Ce qui fonctionne

- M3 générique : sortes finies, signatures d'opérations, termes récursifs typés, lois et moteur de réécriture borné.
- M2 booléen déclaré : constantes, NOT, AND, OR et quelques lois. XOR n'est **pas** une primitive.
- Contrats pour capteurs, assimilation, stockage de croyances, construction de contexte, synthèse, validation, expérience et corroboration.
- Observations sourcées, propositions de croyances, soutien/opposition, état inconnu et contradictions conservées.
- Fermeture locale explicite : domaine fini, déterminisme, stationnarité et fiabilité des observations supposés. Une donnée manquante ne devient jamais fausse.
- Synthèse de programmes compatible avec les exemples, plusieurs hypothèses concurrentes, déduplication sémantique sur le domaine déclaré.
- Sélection de l'expérience maximisant le désaccord entre les candidats.
- Validation de typage et confrontation empirique ; distinction entre contre-exemple, absence de solution sous borne, erreur et épuisement du budget.
- Corroboration conditionnelle uniquement après un test non utilisé pour construire cette hypothèse.
- Retraits explicites, conservation de l'historique, invalidation des évaluations dépendantes et nouvelle synthèse à la demande.
- Journal JSON de la boucle : observations, contextes, hypothèses, rapports, expériences et évaluations.

## Résultats exécutés

| Cas | Résultat |
|---|---|
| Exemple historique `and(and(true,true),true)` | Normalisé en `true` |
| XOR, deux exemples initiaux | Retrouvé après deux requêtes supplémentaires |
| AND, deux exemples initiaux | Retrouvé après deux requêtes supplémentaires |
| OR, trois exemples, sans requête | OR et XOR restent possibles ; abstention sur le cas manquant |
| Ensemble des 16 fonctions booléennes à deux variables | Toutes retrouvées avec au plus trois requêtes après un exemple initial |
| Grille XOR, nouvelle disposition et nouvelle taille | Sortie exacte, sans utiliser les réponses de test pour la synthèse |

Programme XOR obtenu :

```text
and(or(a, b), not(and(a, b)))
```

Les requêtes actives sont une extension expérimentale : le protocole ARC classique ne permet pas de demander librement des labels. Le mode grille fonctionne passivement.

## Structure

| Fichier | Responsabilité |
|---|---|
| `epistemic/algebra.py` | Métalangage, interprétation finie, théories et réécriture |
| `epistemic/model.py` | Objets immuables et provenance, contrats, rapports, évaluations |
| `epistemic/interfaces.py` | Ports Python `Protocol` remplaçables |
| `epistemic/beliefs.py` | Assimilation directe, croyances, rétraction et contexte local |
| `epistemic/inference.py` | Synthèse, choix d'expérience, validateurs et politique de corroboration |
| `epistemic/engine.py` | Orchestration par injection des composants |
| `epistemic/boolean.py` | Déclaration M2 et simulateur de capteur |
| `epistemic/arc.py` | Adaptateur grilles binaires alignées |
| `examples/xor_grid.json` | Tâche démontrable et modifiable |
| `tests/test_framework.py` | Tests de comportement et d'absence de fuite des labels |
| `runs/` | Résultats et traces de l'exécution livrée |

## Exemple SDK

```python
from epistemic import Engine, Problem, ClosurePolicy, Budget
from epistemic.boolean import boolean_theory, TableSensor, domain

problem = Problem('mystery', (('a', 'Bool'), ('b', 'Bool')), 'Bool')
engine = Engine(boolean_theory().language)
# Le simulateur possède la table ; le synthétiseur ne la reçoit jamais.
sensor = TableSensor('mystery', dict(zip(domain(), ('0', '1', '1', '0'))))
engine.ingest(sensor.observe(('0', '0')))
engine.ingest(sensor.observe(('1', '1')))
result = engine.run(problem, ClosurePolicy(domain()), Budget(), sensor, max_queries=2)
for hypothesis in result.search.hypotheses:
    print(hypothesis.term)
print(engine.predict(result, ('0', '1')))
engine.trace.export('trace.json')
```

## Convention M3 → M0

M3 décrit les objets `Sort`, `Operation`, `Term`, `Law`, `Language` et `Theory`. M2 déclare une algèbre particulière, ses tables et ses lois. M1 porte un terme/programme dans ce langage. M0 désigne ici la valeur obtenue dans l'interprétation choisie. Cette dernière est une convention de ce prototype, pas une identité universelle entre niveau MDE et résultat d'exécution.

La sémantique finie est donnée par les tables des opérations. Les lois sont vérifiées exhaustivement contre cette interprétation avant réécriture. Cela valide leur cohérence avec les tables, pas leur vérité dans le monde physique. Les lois ne sont pas encore apprises : ce prototype découvre des **programmes M1** dans un **langage M2 fixé**.

## États et garanties

- `consistent` : accord sur les données déjà utilisées pour synthétiser.
- `corroborated` : typage valide et accord avec au moins une observation supplémentaire ; reste conditionnel.
- `refuted` : contre-exemple dans le contexte évalué.
- `inconclusive` : preuves insuffisantes ou erreur d'exécution.
- `stale` : dépendances modifiées ; nouvelle évaluation requise.

`identified-within-bound` signifie qu'une seule **fonction sur le domaine déclaré** reste représentée dans l'espace exploré. Plusieurs programmes syntaxiquement différents peuvent exprimer cette fonction. Cela ne prouve pas la validité hors domaine.

La synthèse garde un représentant minimal par signature sémantique. Elle explore les compositions par taille croissante, jusqu'à `max_nodes` ou `max_evaluations`. La déduplication est valable ici car les opérations sont pures, totales et compositionnelles. La fermeture porte sur les entrées possibles, jamais sur les sorties inconnues de la cible.

## Ce qui reste volontairement limité

Ce projet est une fondation exécutable, pas un framework universel achevé. Il n'inclut pas de moteur bayésien, de LLM, de SMT, de bruit probabiliste, d'apprentissage de nouveaux langages ou de persistance transactionnelle. Les interfaces permettent de remplacer les composants, mais ces adaptateurs ne sont pas implémentés.

Le contexte de référence utilise l'interprétation directe des observations. Une assimilation non littérale doit fournir un constructeur de contexte et des validateurs compatibles. Le graphe conserve les soutiens et oppositions aux énoncés ; il n'effectue pas une clôture logique générale. La révision invalide les évaluations dépendantes et reconstruit les candidats à la prochaine exécution ; elle n'est pas un solveur incrémental général de justification.

Les tables d'interprétation doivent être finies. Le coût croît rapidement avec le nombre de variables et d'opérations. Le budget compte les évaluations de candidats, pas un délai mural strict. Les identités de version sont déclarées par le développeur : changer un langage exige de changer sa version. La provenance du simulateur est explicite mais non authentifiée cryptographiquement.

Dans le cas grille, la décomposition en deux panneaux alignés et l'hypothèse d'une même règle pour chaque cellule sont **données**. Les quatre combinaisons booléennes figurent dans la grille d'entraînement. Le test démontre le transfert de la règle à une nouvelle disposition, pas la découverte autonome des objets ou des représentations visuelles d'ARC.

Les contrats sont déclaratifs ; les contrôles réellement exécutés sont ceux des adaptateurs. La cohérence des tables et des lois est vérifiée, la confluence générale des réécritures ne l'est pas. Les sorties des tests sont séparées de l'apprentissage, mais le processus Python n'est pas un bac à sable contre du code malveillant.

## Prochaine extension cohérente

Introduire plusieurs représentations concurrentes pour une grille (pointwise, voisinage, ligne), puis traiter le choix de représentation et du programme comme une hypothèse composée. Les erreurs permettront alors de distinguer « mauvais programme dans le bon langage » et « langage insuffisant ».

## Extension floue testée

```bash
python -m epistemic.fuzzy_demo --output runs/fuzzy
```

Les degrés sont `0, 0.25, 0.5, 0.75, 1`. Aucun changement au noyau M3 ni au moteur de synthèse n'a été nécessaire : seules une algèbre M2 et des expériences ont été ajoutées.

| Cible | Règle retrouvée | Cas réservés réussis |
|---|---|---|
| Conjonction minimum | `min(a,b)` | 20/20 |
| Produit discrétisé | `product_floor(a,b)` | 20/20 |
| Inhibition | `min(a,not(b))` | 21/21 |
| Voisins et densité | `min(a,min(b,c))` | 117/117 |

Minimum et produit sont compatibles avec les quatre exemples booléens initiaux. Le planificateur demande `(0.25,0.25)` : minimum prédit `0.25`, le produit arrondi vers le bas prédit `0`. Cette observation suffit dans la grammaire limitée à trois nœuds. Le produit continu donnerait `0.0625` : l'arrondi est explicite, pas une assimilation au produit exact.

Les deux autres expériences utilisent seulement min/max/complément comme opérateurs : leur identification dépend donc de ce biais de langage et de la borne de taille. Les observations de validation sont des entrées non vues, choisies dans le même domaine discret, avec des réponses exactes de simulateur. Ce n'est pas une mesure de robustesse au bruit des capteurs ni une preuve sur le continu.

La règle de densité produit `0.25` pour des voisins à `0.75` et une densité à `0.25`, au lieu du `0.75` de la règle fondée seulement sur les voisins. Les degrés d'activation et de densité sont déjà fournis ; aucune perception d'image n'est apprise. `SOFT_GE` et l'apprentissage d'un seuil ne sont pas encore implémentés.

20 tests passent au total. Un test confirme notamment que `product_floor` n'est pas associatif : il ne faut pas lui transférer silencieusement les lois du produit continu. Ces degrés de satisfaction ne sont pas des probabilités de croyance.

## Plan de recherche

Voir [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) : commencer avec M2 fixé pour distinguer expressivité, recherche, sélection et ambiguïté ; ouvrir ensuite les représentations et les abstractions, avec un plan permettant de mesurer leurs interactions.

Les traces `runs/` sont générées localement et exclues de Git. Les commandes ci-dessus les reproduisent.
