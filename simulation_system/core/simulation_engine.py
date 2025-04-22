#!/usr/bin/env python3
"""
Module définissant le moteur de simulation qui coordonne l'ensemble du processus.
"""

import os
import json
import logging
from datetime import datetime
import pandas as pd
import traceback
import uuid

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimulationEngine:
    """Coordonne l'ensemble du processus de simulation."""
    
    def __init__(self, data_source, processor, model, output_handler):
        """
        Initialise un moteur de simulation avec ses composants.
        
        Args:
            data_source: Instance d'une classe dérivée de DataSource
            processor: Instance de DataProcessor
            model: Instance de ModelSimulator
            output_handler: Instance de OutputHandler
        """
        self.data_source = data_source
        self.processor = processor
        self.model = model
        self.output_handler = output_handler
        self.simulation_history = []
        
        # Identifiant unique pour la session de simulation
        self.session_id = str(uuid.uuid4())
        logger.info(f"Moteur de simulation initialisé avec ID de session: {self.session_id}")
    
    def run_simulation(self, parameters=None):
        """
        Exécute une simulation complète avec les composants configurés.
        
        Args:
            parameters (dict, optional): Paramètres pour cette exécution. Par défaut à None.
            
        Returns:
            dict: Résultats de la simulation
        """
        parameters = parameters or {}
        start_time = datetime.now()
        logger.info(f"Démarrage de la simulation avec paramètres: {parameters}")
        
        run_id = str(uuid.uuid4())
        
        # Métadonnées de la simulation
        simulation_metadata = {
            "run_id": run_id,
            "session_id": self.session_id,
            "start_time": start_time.isoformat(),
            "parameters": parameters,
            "data_source_type": type(self.data_source).__name__,
            "model_type": self.model.model_type,
            "simulation_mode": self.model.simulation_mode
        }
        
        try:
            # 1. Récupérer les données
            logger.info("Étape 1: Récupération des données")
            raw_data = self.data_source.get_data()
            
            if raw_data is None:
                logger.error("Échec de la récupération des données")
                return self._handle_simulation_error("Échec de la récupération des données", simulation_metadata)
            
            # Validation des données
            if not self.data_source.validate():
                logger.warning("Validation des données échouée, mais continue avec les données disponibles")
            
            # 2. Traiter les données
            logger.info("Étape 2: Traitement des données")
            try:
                processed_data = self.processor.prepare_for_model(raw_data)
                
                if processed_data is None or (isinstance(processed_data, pd.DataFrame) and len(processed_data) == 0):
                    logger.error("Échec du traitement des données")
                    return self._handle_simulation_error("Échec du traitement des données", simulation_metadata)
            except Exception as e:
                logger.error(f"Erreur lors du traitement des données: {str(e)}")
                return self._handle_simulation_error(f"Erreur de traitement: {str(e)}", simulation_metadata)
            
            # 3. Exécuter le modèle
            logger.info("Étape 3: Exécution du modèle")
            try:
                predictions = self.model.predict(processed_data)
                
                if not predictions:
                    logger.error("Échec de la génération des prédictions")
                    return self._handle_simulation_error("Échec de la génération des prédictions", simulation_metadata)
            except Exception as e:
                logger.error(f"Erreur lors de l'exécution du modèle: {str(e)}")
                return self._handle_simulation_error(f"Erreur du modèle: {str(e)}", simulation_metadata)
            
            # 4. Évaluer les résultats (avec des données simulées si nécessaire)
            logger.info("Étape 4: Évaluation des performances")
            try:
                performance = self.model.evaluate_performance(predictions)
            except Exception as e:
                logger.error(f"Erreur lors de l'évaluation des performances: {str(e)}")
                performance = {"error": str(e), "evaluation_mode": "failed"}
            
            # 5. Assembler les résultats
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            results = {
                "predictions": predictions,
                "performance": performance,
                "metadata": {
                    **simulation_metadata,
                    "end_time": end_time.isoformat(),
                    "execution_time_seconds": execution_time
                }
            }
            
            # 6. Générer et sauvegarder les sorties
            logger.info("Étape 5: Formatage et sauvegarde des résultats")
            try:
                formatted_output = self.output_handler.format_output(results)
                output_path = self.output_handler.save_output(formatted_output)
                results["metadata"]["output_path"] = output_path
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde des résultats: {str(e)}")
                results["metadata"]["output_error"] = str(e)
            
            # 7. Enregistrer l'historique
            self.simulation_history.append({
                "run_id": run_id,
                "timestamp": end_time.isoformat(),
                "parameters": parameters,
                "performance_summary": performance,
                "execution_time_seconds": execution_time,
                "success": True
            })
            
            logger.info(f"Simulation terminée avec succès en {execution_time:.2f} secondes")
            return results
        
        except Exception as e:
            # Gestion des erreurs non capturées
            logger.error(f"Erreur inattendue pendant la simulation: {str(e)}")
            logger.error(traceback.format_exc())
            return self._handle_simulation_error(str(e), simulation_metadata, traceback.format_exc())
    
    def _handle_simulation_error(self, error_message, metadata, traceback_info=None):
        """
        Gère les erreurs de simulation et enregistre les informations.
        
        Args:
            error_message (str): Message d'erreur
            metadata (dict): Métadonnées de la simulation
            traceback_info (str, optional): Informations de traceback. Par défaut à None.
            
        Returns:
            dict: Résultats d'erreur
        """
        end_time = datetime.now()
        start_time = datetime.fromisoformat(metadata["start_time"])
        execution_time = (end_time - start_time).total_seconds()
        
        error_results = {
            "error": error_message,
            "metadata": {
                **metadata,
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "success": False
            }
        }
        
        if traceback_info:
            error_results["metadata"]["traceback"] = traceback_info
        
        # Enregistrer l'erreur dans l'historique
        self.simulation_history.append({
            "run_id": metadata["run_id"],
            "timestamp": end_time.isoformat(),
            "parameters": metadata.get("parameters", {}),
            "error": error_message,
            "execution_time_seconds": execution_time,
            "success": False
        })
        
        logger.info(f"Simulation terminée avec erreur en {execution_time:.2f} secondes: {error_message}")
        return error_results
    
    def run_batch_simulations(self, parameter_sets):
        """
        Exécute plusieurs simulations avec différents ensembles de paramètres.
        
        Args:
            parameter_sets (list): Liste de dictionnaires contenant des paramètres
            
        Returns:
            list: Liste des résultats de simulation
        """
        if not parameter_sets:
            logger.warning("Aucun ensemble de paramètres fourni pour les simulations par lots")
            return []
        
        logger.info(f"Démarrage de {len(parameter_sets)} simulations par lots")
        batch_results = []
        
        for i, params in enumerate(parameter_sets):
            logger.info(f"Simulation par lots {i+1}/{len(parameter_sets)} avec paramètres: {params}")
            result = self.run_simulation(params)
            batch_results.append(result)
        
        logger.info(f"Simulations par lots terminées: {len(batch_results)} exécutions")
        return batch_results
    
    def generate_simulation_report(self):
        """
        Génère un rapport complet sur les simulations effectuées.
        
        Returns:
            dict: Rapport de simulation
        """
        if not self.simulation_history:
            logger.warning("Aucun historique de simulation disponible pour le rapport")
            return {"error": "Aucun historique de simulation disponible"}
        
        logger.info(f"Génération du rapport pour {len(self.simulation_history)} simulations")
        return self.output_handler.generate_report(self.simulation_history)
    
    def get_simulation_history(self):
        """
        Retourne l'historique des simulations.
        
        Returns:
            list: Historique des simulations
        """
        return self.simulation_history
    
    def export_simulation_history(self, format="json", destination=None):
        """
        Exporte l'historique des simulations dans un fichier.
        
        Args:
            format (str, optional): Format d'export ('json', 'csv'). Par défaut à "json".
            destination (str, optional): Chemin de destination. Par défaut à None.
            
        Returns:
            str: Chemin du fichier exporté
        """
        if not self.simulation_history:
            logger.warning("Aucun historique de simulation à exporter")
            return None
        
        if not destination:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = f"simulation_history_{timestamp}.{format}"
        
        temp_handler = self.output_handler
        if format != self.output_handler.output_format or destination != self.output_handler.destination:
            temp_handler = type(self.output_handler)(format, destination)
        
        formatted_data = temp_handler.format_output(self.simulation_history)
        export_path = temp_handler.save_output(formatted_data)
        
        logger.info(f"Historique de simulation exporté: {export_path}")
        return export_path

# Exemple d'utilisation pour les tests
if __name__ == "__main__":
    # Imports nécessaires pour le test
    from data_source import FileDataSource, APIDataSource
    from data_processor import DataProcessor
    from model_simulator import ModelSimulator
    from output_handler import OutputHandler
    
    # Créer les composants pour le moteur de simulation
    data_source = FileDataSource("../attached_assets/cost_2025-01-30_2025-03-01.csv")
    processor = DataProcessor({
        "remove_duplicates": True,
        "handle_missing": "mean"
    })
    model = ModelSimulator("sentiment_analysis", simulation_mode=True)
    output_handler = OutputHandler("json", "simulation_results.json")
    
    # Créer et exécuter le moteur de simulation
    engine = SimulationEngine(data_source, processor, model, output_handler)
    results = engine.run_simulation()
    
    print(f"Simulation terminée avec succès: {results['metadata']['success']}")
    print(f"Temps d'exécution: {results['metadata']['execution_time_seconds']:.2f} secondes")
    
    # Exécuter une simulation par lots
    batch_params = [
        {"threshold": 0.5, "iterations": 100},
        {"threshold": 0.7, "iterations": 100},
        {"threshold": 0.9, "iterations": 100}
    ]
    batch_results = engine.run_batch_simulations(batch_params)
    
    # Générer un rapport
    report = engine.generate_simulation_report()
    print(f"Rapport généré: {report['report_directory'] if 'report_directory' in report else 'erreur'}")
    
    # Exporter l'historique
    history_path = engine.export_simulation_history()
    print(f"Historique exporté: {history_path}")