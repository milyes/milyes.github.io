#!/usr/bin/env python3
"""
Exemple d'utilisation du système de simulation IA.
Montre comment configurer et exécuter des simulations avec différentes sources de données et modèles.
"""

import os
import sys
import logging
import json
from datetime import datetime

# Ajouter le dossier parent au path pour pouvoir importer le package simulation_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import des classes du système de simulation
from simulation_system.core import (
    FileDataSource, APIDataSource, SensorDataSource,
    DataProcessor, ModelSimulator, OutputHandler, SimulationEngine
)

def run_cost_data_regression():
    """
    Exemple: Régression sur les données de coût CSV.
    """
    logger.info("Exemple: Régression sur les données de coût CSV")
    
    # 1. Configurer la source de données (CSV)
    csv_path = "../attached_assets/cost_2025-01-30_2025-03-01.csv"
    if not os.path.exists(csv_path):
        logger.error(f"Fichier CSV non trouvé: {csv_path}")
        return
    
    data_source = FileDataSource(csv_path)
    
    # 2. Configurer le processeur de données
    cleaning_rules = {
        "remove_duplicates": True,
        "handle_missing": "mean"
    }
    transformation_rules = {
        "normalization": "standard"
    }
    processor = DataProcessor(cleaning_rules, transformation_rules)
    
    # 3. Configurer le modèle (changer pour régression qui est plus adapté aux données CSV)
    model = ModelSimulator("regression", 
                           parameters={"base_value": 25, "noise_level": 5},
                           simulation_mode=True)
    
    # 4. Configurer le gestionnaire de sorties
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"cost_data_regression_{timestamp}.json")
    output_handler = OutputHandler("json", output_path)
    
    # 5. Créer et exécuter le moteur de simulation
    engine = SimulationEngine(data_source, processor, model, output_handler)
    results = engine.run_simulation()
    
    # 6. Afficher les résultats
    logger.info(f"Simulation terminée avec succès: {results['metadata'].get('success', False)}")
    logger.info(f"Temps d'exécution: {results['metadata'].get('execution_time_seconds', 0):.2f} secondes")
    logger.info(f"Résultats sauvegardés dans: {results['metadata'].get('output_path', 'non disponible')}")
    
    # 7. Générer un rapport
    report = engine.generate_simulation_report()
    logger.info(f"Rapport généré: {report.get('report_directory', 'erreur')}")
    
    return results

def run_api_data_summarization():
    """
    Exemple: Résumé de texte avec données d'API simulées.
    """
    logger.info("Exemple: Résumé de texte avec données d'API simulées")
    
    # 1. Configurer la source de données (API simulée)
    data_source = APIDataSource(
        "https://api.example.com/data",
        parameters={"limit": 10},
        simulation_mode=True
    )
    
    # 2. Configurer le processeur de données
    processor = DataProcessor({
        "handle_missing": "drop",
        "remove_outliers": True
    })
    
    # 3. Configurer le modèle (résumé de texte en mode simulation)
    model = ModelSimulator("summarization", 
                           parameters={"max_tokens": 100},
                           simulation_mode=True)
    
    # 4. Configurer le gestionnaire de sorties
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"summarization_{timestamp}.json")
    output_handler = OutputHandler("json", output_path)
    
    # 5. Créer et exécuter le moteur de simulation
    engine = SimulationEngine(data_source, processor, model, output_handler)
    results = engine.run_simulation()
    
    # 6. Afficher les résultats
    logger.info(f"Simulation terminée avec succès: {results['metadata'].get('success', False)}")
    logger.info(f"Temps d'exécution: {results['metadata'].get('execution_time_seconds', 0):.2f} secondes")
    
    return results

def run_sensor_data_regression():
    """
    Exemple: Régression sur des données de capteurs simulées.
    """
    logger.info("Exemple: Régression sur des données de capteurs simulées")
    
    # 1. Configurer la source de données (capteurs simulés)
    data_source = SensorDataSource("temperature", {
        "num_readings": 100,
        "range": (15, 35),
        "variance": 2.5
    })
    
    # 2. Configurer le processeur de données
    processor = DataProcessor({
        "handle_missing": "mean",
        "remove_outliers": True,
        "outlier_method": "zscore",
        "outlier_threshold": 2.5
    }, {
        "normalization": "minmax"
    })
    
    # 3. Configurer le modèle (régression en mode simulation)
    model = ModelSimulator("regression", 
                           parameters={"base_value": 25, "noise_level": 5},
                           simulation_mode=True)
    
    # 4. Configurer le gestionnaire de sorties
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"regression_{timestamp}.json")
    output_handler = OutputHandler("json", output_path)
    
    # 5. Créer et exécuter le moteur de simulation
    engine = SimulationEngine(data_source, processor, model, output_handler)
    
    # 6. Exécuter plusieurs simulations avec différents paramètres
    batch_params = [
        {"threshold": 0.5, "iterations": 10},
        {"threshold": 0.7, "iterations": 10},
        {"threshold": 0.9, "iterations": 10}
    ]
    
    batch_results = engine.run_batch_simulations(batch_params)
    logger.info(f"Simulations par lots terminées: {len(batch_results)} exécutions")
    
    # 7. Générer un rapport
    report = engine.generate_simulation_report()
    logger.info(f"Rapport généré: {report.get('report_directory', 'erreur')}")
    
    # 8. Exporter l'historique
    history_path = engine.export_simulation_history()
    logger.info(f"Historique exporté: {history_path}")
    
    return batch_results

def run_chatbot_simulation():
    """
    Exemple: Simulation de chatbot.
    """
    logger.info("Exemple: Simulation de chatbot")
    
    # Utilisons un exemple simple pour le chatbot
    # Le modèle prend directement du texte en entrée, pas besoin de DataSource
    # On va créer une classe spéciale qui retourne juste une chaîne de texte
    
    class TextSource(FileDataSource):
        def __init__(self, text):
            self.text = text
            self.data = None
        
        def get_data(self):
            return self.text
        
        def validate(self):
            return True
    
    # Quelques exemples de questions pour le chatbot
    questions = [
        "Bonjour, comment allez-vous?",
        "Qu'est-ce que l'intelligence artificielle?",
        "Pouvez-vous m'aider avec un problème de programmation?",
        "Merci pour votre aide!"
    ]
    
    data_source = TextSource(questions[0])  # On commence avec la première question
    
    # Créer un processeur spécial pour le texte qui ne fait aucun traitement
    class TextProcessor(DataProcessor):
        def prepare_for_model(self, data):
            # Pas de traitement pour le texte, on le retourne tel quel
            return data
    
    # Utiliser notre processeur spécial
    processor = TextProcessor()
    
    # Configurer le modèle chatbot
    model = ModelSimulator("chatbot", simulation_mode=True)
    
    # Configurer le gestionnaire de sorties
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"chatbot_{timestamp}.json")
    output_handler = OutputHandler("json", output_path)
    
    # Créer le moteur de simulation
    engine = SimulationEngine(data_source, processor, model, output_handler)
    
    # Exécuter une simulation pour chaque question
    all_results = []
    for question in questions:
        # Mettre à jour la question
        engine.data_source = TextSource(question)
        
        # Exécuter la simulation
        result = engine.run_simulation({"question": question})
        
        # Afficher la réponse
        if "predictions" in result and "response" in result["predictions"]:
            logger.info(f"Q: {question}")
            logger.info(f"R: {result['predictions']['response']}")
        
        all_results.append(result)
    
    # Générer un rapport
    report = engine.generate_simulation_report()
    logger.info(f"Rapport de chatbot généré: {report.get('report_directory', 'erreur')}")
    
    return all_results

if __name__ == "__main__":
    # Créer le dossier de sortie
    os.makedirs("output", exist_ok=True)
    
    # Exécuter les exemples
    logger.info("Démarrage des exemples de simulation")
    
    try:
        # Exemple 1: Régression sur données de coût
        cost_regression_results = run_cost_data_regression()
        
        # Exemple 2: Résumé de texte
        summarization_results = run_api_data_summarization()
        
        # Exemple 3: Régression sur données de capteurs
        regression_results = run_sensor_data_regression()
        
        # Exemple 4: Simulation de chatbot
        chatbot_results = run_chatbot_simulation()
        
        logger.info("Tous les exemples ont été exécutés avec succès")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des exemples: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())