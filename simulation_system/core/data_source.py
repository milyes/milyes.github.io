#!/usr/bin/env python3
"""
Module définissant les classes pour les sources de données dans le système de simulation IA.
"""

import os
import json
import csv
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime
import requests
import random
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataSource(ABC):
    """Interface abstraite pour toutes les sources de données."""
    
    @abstractmethod
    def get_data(self):
        """
        Récupère les données depuis la source.
        
        Returns:
            dict ou DataFrame: Les données récupérées
        """
        pass
    
    @abstractmethod
    def validate(self):
        """
        Valide l'intégrité des données.
        
        Returns:
            bool: True si les données sont valides, False sinon
        """
        pass


class FileDataSource(DataSource):
    """Source de données basée sur des fichiers (CSV, JSON, etc.)"""
    
    def __init__(self, file_path, file_type="csv"):
        """
        Initialise une source de données basée sur un fichier.
        
        Args:
            file_path (str): Chemin vers le fichier
            file_type (str, optional): Type de fichier ('csv', 'json', etc.). Par défaut à "csv".
        """
        self.file_path = file_path
        self.file_type = file_type.lower()
        self.data = None
        
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            logger.warning(f"Le fichier {file_path} n'existe pas.")
    
    def get_data(self):
        """
        Récupère les données depuis le fichier.
        
        Returns:
            pd.DataFrame: Les données du fichier sous forme de DataFrame pandas
        """
        try:
            if self.file_type == "csv":
                self.data = pd.read_csv(self.file_path)
            elif self.file_type == "json":
                with open(self.file_path, 'r') as f:
                    raw_data = json.load(f)
                self.data = pd.DataFrame(raw_data)
            else:
                logger.error(f"Type de fichier non supporté: {self.file_type}")
                return None
            
            logger.info(f"Données chargées avec succès: {len(self.data)} enregistrements")
            return self.data
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {str(e)}")
            return None
    
    def validate(self):
        """
        Valide l'intégrité des données du fichier.
        
        Returns:
            bool: True si les données sont valides, False sinon
        """
        if self.data is None:
            self.get_data()
            
        if self.data is None or len(self.data) == 0:
            logger.warning("Données vides ou invalides")
            return False
        
        # Vérifier les valeurs manquantes
        missing_values = self.data.isnull().sum().sum()
        if missing_values > 0:
            logger.warning(f"Le dataset contient {missing_values} valeurs manquantes")
        
        # Vérifier si le DataFrame a des colonnes
        if len(self.data.columns) == 0:
            logger.warning("Le dataset ne contient aucune colonne")
            return False
        
        return True


class APIDataSource(DataSource):
    """Source de données basée sur des API externes."""
    
    def __init__(self, api_url, auth_token=None, parameters=None, simulation_mode=False):
        """
        Initialise une source de données basée sur une API.
        
        Args:
            api_url (str): URL de l'API
            auth_token (str, optional): Token d'authentification. Par défaut à None.
            parameters (dict, optional): Paramètres pour la requête API. Par défaut à None.
            simulation_mode (bool, optional): Si True, simule les réponses API. Par défaut à False.
        """
        self.api_url = api_url
        self.auth_token = auth_token
        self.parameters = parameters or {}
        self.simulation_mode = simulation_mode
        self.data = None
    
    def get_data(self):
        """
        Récupère les données depuis l'API ou génère des données simulées.
        
        Returns:
            dict ou pd.DataFrame: Les données de l'API
        """
        if self.simulation_mode:
            logger.info("Mode simulation activé - génération de données simulées")
            return self._simulate_api_response()
        
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f"Bearer {self.auth_token}"
            
            response = requests.get(
                self.api_url,
                params=self.parameters,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.data = response.json()
                logger.info("Données API récupérées avec succès")
                
                # Convertir en DataFrame si c'est un dictionnaire ou une liste
                if isinstance(self.data, (dict, list)):
                    self.data = pd.DataFrame(self.data)
                
                return self.data
            else:
                logger.error(f"Erreur API: {response.status_code} - {response.text}")
                # Fallback en mode simulation en cas d'erreur API
                logger.warning("Passage en mode simulation suite à une erreur API")
                return self._simulate_api_response()
        
        except Exception as e:
            logger.error(f"Erreur lors de l'appel API: {str(e)}")
            # Fallback en mode simulation en cas d'exception
            logger.warning("Passage en mode simulation suite à une exception")
            return self._simulate_api_response()
    
    def _simulate_api_response(self):
        """
        Génère une réponse API simulée.
        
        Returns:
            pd.DataFrame: Données simulées
        """
        # Créer un DataFrame simulé avec une structure qui dépend des paramètres
        simulated_data = {
            "id": list(range(1, 21)),
            "value": [random.uniform(0, 100) for _ in range(20)],
            "category": [random.choice(["A", "B", "C"]) for _ in range(20)],
            "timestamp": [datetime.now().isoformat() for _ in range(20)]
        }
        
        self.data = pd.DataFrame(simulated_data)
        return self.data
    
    def validate(self):
        """
        Valide l'intégrité des données de l'API.
        
        Returns:
            bool: True si les données sont valides, False sinon
        """
        if self.data is None:
            self.get_data()
            
        if self.data is None:
            logger.warning("Impossible de valider des données nulles")
            return False
        
        # Si les données sont un DataFrame, vérifier sa structure
        if isinstance(self.data, pd.DataFrame):
            if len(self.data) == 0:
                logger.warning("Le dataset est vide")
                return False
            
            # Vérifier les valeurs manquantes
            missing_values = self.data.isnull().sum().sum()
            if missing_values > 0:
                logger.warning(f"Le dataset contient {missing_values} valeurs manquantes")
        
        return True


class SensorDataSource(DataSource):
    """Simulation de données provenant de capteurs IoT."""
    
    def __init__(self, sensor_type, simulation_params=None):
        """
        Initialise une source de données simulant des capteurs.
        
        Args:
            sensor_type (str): Type de capteur ('temperature', 'humidity', etc.)
            simulation_params (dict, optional): Paramètres pour la simulation. Par défaut à None.
        """
        self.sensor_type = sensor_type
        self.simulation_params = simulation_params or {}
        self.data = None
        
        # Paramètres par défaut selon le type de capteur
        if self.sensor_type == "temperature":
            self.default_range = (15, 30)  # Plage de température en °C
            self.default_variance = 2.0    # Variance des fluctuations
        elif self.sensor_type == "humidity":
            self.default_range = (30, 90)  # Plage d'humidité en %
            self.default_variance = 5.0    # Variance des fluctuations
        elif self.sensor_type == "pressure":
            self.default_range = (990, 1020)  # Plage de pression en hPa
            self.default_variance = 3.0       # Variance des fluctuations
        else:
            self.default_range = (0, 100)
            self.default_variance = 1.0
    
    def get_data(self):
        """
        Génère des données simulées de capteurs.
        
        Returns:
            pd.DataFrame: Données simulées de capteur
        """
        # Récupérer les paramètres de simulation
        num_readings = self.simulation_params.get('num_readings', 100)
        value_range = self.simulation_params.get('range', self.default_range)
        variance = self.simulation_params.get('variance', self.default_variance)
        
        # Générer des timestamps
        timestamps = [
            datetime.now().replace(
                minute=i % 60, 
                second=0, 
                microsecond=0
            ).isoformat() 
            for i in range(num_readings)
        ]
        
        # Générer des valeurs de base avec tendance
        base_values = [
            value_range[0] + (value_range[1] - value_range[0]) * (i / num_readings)
            for i in range(num_readings)
        ]
        
        # Ajouter des fluctuations aléatoires
        values = [
            max(value_range[0], min(value_range[1], v + random.uniform(-variance, variance)))
            for v in base_values
        ]
        
        # Créer un DataFrame avec les données simulées
        simulated_data = {
            "timestamp": timestamps,
            "value": values,
            "sensor_type": self.sensor_type,
            "unit": self._get_unit_for_sensor_type()
        }
        
        self.data = pd.DataFrame(simulated_data)
        logger.info(f"Génération de {num_readings} lectures simulées pour capteur de type {self.sensor_type}")
        
        return self.data
    
    def _get_unit_for_sensor_type(self):
        """
        Retourne l'unité correspondant au type de capteur.
        
        Returns:
            str: Unité de mesure
        """
        units = {
            "temperature": "°C",
            "humidity": "%",
            "pressure": "hPa",
            "light": "lux",
            "sound": "dB",
            "motion": "events"
        }
        return units.get(self.sensor_type, "unité")
    
    def validate(self):
        """
        Valide l'intégrité des données de capteur simulées.
        
        Returns:
            bool: True si les données sont valides, False sinon
        """
        if self.data is None:
            self.get_data()
            
        if len(self.data) == 0:
            logger.warning("Les données de capteur simulées sont vides")
            return False
        
        # Vérifier que les valeurs sont dans la plage attendue
        value_range = self.simulation_params.get('range', self.default_range)
        values_in_range = (
            (self.data['value'] >= value_range[0]) &
            (self.data['value'] <= value_range[1])
        ).all()
        
        if not values_in_range:
            logger.warning("Certaines valeurs de capteur sont hors de la plage attendue")
        
        return True

# Exemple d'utilisation simple pour les tests
if __name__ == "__main__":
    # Test avec un fichier CSV existant
    file_source = FileDataSource("attached_assets/cost_2025-01-30_2025-03-01.csv")
    data = file_source.get_data()
    if data is not None:
        print(f"Données du fichier: {len(data)} enregistrements")
        print(data.head())
    
    # Test avec une API simulée
    api_source = APIDataSource("https://api.example.com/data", simulation_mode=True)
    api_data = api_source.get_data()
    if api_data is not None:
        print(f"Données API simulées: {len(api_data)} enregistrements")
        print(api_data.head())
    
    # Test avec un capteur simulé
    sensor_source = SensorDataSource("temperature", {"num_readings": 10})
    sensor_data = sensor_source.get_data()
    if sensor_data is not None:
        print(f"Données de capteur simulées: {len(sensor_data)} enregistrements")
        print(sensor_data.head())