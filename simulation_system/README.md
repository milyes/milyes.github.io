# Système de Simulation IA Automatique

Un système modulaire et extensible pour la simulation, le traitement et l'analyse de données avec des modèles d'IA, conçu pour fonctionner efficacement avec des ressources limitées.

## Caractéristiques principales

- **Architecture modulaire** : Composants indépendants et interchangeables
- **Mode simulation** : Fonctionnement sans API externe pour économiser des coûts
- **Sources de données variées** : Fichiers, API, capteurs simulés
- **Traitement de données avancé** : Nettoyage, transformation, normalisation
- **Modèles d'IA flexibles** : Chatbot, analyse de sentiment, résumé de texte, classification, régression
- **Génération de rapports** : Métriques, visualisations, historique
- **Gestion d'erreurs robuste** : Fallback automatique, traçabilité complète

## Architecture

Le système est organisé en plusieurs composants clés :

1. **Sources de données** (`DataSource`)
   - Récupération des données depuis différentes sources
   - Validation de l'intégrité des données

2. **Processeur de données** (`DataProcessor`)
   - Nettoyage et préparation des données 
   - Transformation et normalisation

3. **Simulateur de modèle** (`ModelSimulator`)
   - Génération de prédictions réelles ou simulées
   - Évaluation des performances

4. **Gestionnaire de sorties** (`OutputHandler`)
   - Formatage des résultats en différents formats (JSON, CSV, XLSX)
   - Génération de rapports et visualisations

5. **Moteur de simulation** (`SimulationEngine`)
   - Coordination de l'ensemble du processus
   - Gestion de l'historique des simulations

## Guides d'utilisation

### Configuration basique

```python
from simulation_system.core import (
    FileDataSource, DataProcessor, ModelSimulator,
    OutputHandler, SimulationEngine
)

# 1. Configurer la source de données
data_source = FileDataSource("chemin/vers/donnees.csv")

# 2. Configurer le processeur de données
processor = DataProcessor(
    cleaning_rules={"remove_duplicates": True, "handle_missing": "mean"},
    transformation_rules={"normalization": "standard"}
)

# 3. Configurer le modèle (en mode simulation)
model = ModelSimulator("sentiment_analysis", simulation_mode=True)

# 4. Configurer le gestionnaire de sorties
output_handler = OutputHandler("json", "resultats_simulation.json")

# 5. Créer et exécuter le moteur de simulation
engine = SimulationEngine(data_source, processor, model, output_handler)
results = engine.run_simulation()
```

### Simulation par lots

```python
# Exécuter plusieurs simulations avec différents paramètres
batch_params = [
    {"threshold": 0.5, "iterations": 100},
    {"threshold": 0.7, "iterations": 100},
    {"threshold": 0.9, "iterations": 100}
]

batch_results = engine.run_batch_simulations(batch_params)

# Générer un rapport global
report = engine.generate_simulation_report()
```

### Utilisation du mode API

Pour utiliser le mode API avec OpenAI (nécessite une clé API valide) :

```python
import os
os.environ["OPENAI_API_KEY"] = "votre-clé-api"

# Configurer le modèle en mode API
model = ModelSimulator("chatbot", simulation_mode=False)
```

## Types de modèles supportés

1. **Chatbot** : Génération de réponses textuelles
2. **Analyse de sentiment** : Évaluation du sentiment d'un texte
3. **Résumé de texte** : Génération de résumés concis
4. **Classification** : Prédiction de catégories
5. **Régression** : Prédiction de valeurs continues

## Exemples

Voir le fichier `example.py` pour des exemples complets d'utilisation du système avec différentes configurations.

## Installation des dépendances

Le système nécessite les bibliothèques Python suivantes :
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- openai (optionnel, pour le mode API)

## Bonnes pratiques

1. **Commencer en mode simulation** : Développez et testez votre système en mode simulation avant de passer au mode API pour économiser des coûts.
2. **Validation des données** : Assurez-vous que vos données sont validées avant traitement.
3. **Gestion des erreurs** : Implémentez une gestion d'erreurs appropriée, le système offre des mécanismes de fallback automatiques.
4. **Paramétrage** : Utilisez les paramètres pour affiner le comportement des composants selon vos besoins.
5. **Historique** : Exploitez l'historique des simulations pour améliorer vos processus.