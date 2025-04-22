#!/usr/bin/env python3
"""
Module définissant les classes pour le traitement et la préparation des données
dans le système de simulation IA.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    """Traitement et préparation des données pour l'analyse."""
    
    def __init__(self, cleaning_rules=None, transformation_rules=None):
        """
        Initialise un processeur de données avec des règles de nettoyage et de transformation.
        
        Args:
            cleaning_rules (dict, optional): Règles de nettoyage des données. 
                Ex: {"remove_duplicates": True, "handle_missing": "mean"}
            transformation_rules (dict, optional): Règles de transformation des données.
                Ex: {"normalization": "standard", "text_processing": True}
        """
        self.cleaning_rules = cleaning_rules or {}
        self.transformation_rules = transformation_rules or {}
        self.standard_scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
    
    def clean_data(self, data):
        """
        Nettoie les données selon les règles définies.
        
        Args:
            data (pd.DataFrame): Les données à nettoyer
            
        Returns:
            pd.DataFrame: Les données nettoyées
        """
        if not isinstance(data, pd.DataFrame):
            logger.warning("Les données doivent être un DataFrame pandas")
            return data
        
        cleaned_data = data.copy()
        
        # Gestion des duplications
        if self.cleaning_rules.get('remove_duplicates', False):
            original_len = len(cleaned_data)
            cleaned_data = cleaned_data.drop_duplicates()
            duplicates_removed = original_len - len(cleaned_data)
            if duplicates_removed > 0:
                logger.info(f"Suppression de {duplicates_removed} lignes dupliquées")
        
        # Gestion des valeurs manquantes
        missing_handling = self.cleaning_rules.get('handle_missing', None)
        if missing_handling:
            missing_count = cleaned_data.isnull().sum().sum()
            
            if missing_count > 0:
                logger.info(f"Traitement de {missing_count} valeurs manquantes avec méthode '{missing_handling}'")
                
                if missing_handling == "drop":
                    # Supprimer les lignes avec des valeurs manquantes
                    cleaned_data = cleaned_data.dropna()
                
                elif missing_handling == "mean":
                    # Remplacer les valeurs manquantes par la moyenne (colonnes numériques)
                    numeric_cols = cleaned_data.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        if cleaned_data[col].isnull().sum() > 0:
                            cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].mean())
                
                elif missing_handling == "median":
                    # Remplacer les valeurs manquantes par la médiane (colonnes numériques)
                    numeric_cols = cleaned_data.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        if cleaned_data[col].isnull().sum() > 0:
                            cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].median())
                
                elif missing_handling == "mode":
                    # Remplacer les valeurs manquantes par le mode (colonnes catégorielles)
                    for col in cleaned_data.columns:
                        if cleaned_data[col].isnull().sum() > 0:
                            cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].mode()[0])
                
                elif missing_handling == "zero":
                    # Remplacer les valeurs manquantes par zéro
                    cleaned_data = cleaned_data.fillna(0)
                
                else:
                    logger.warning(f"Méthode de gestion des valeurs manquantes non reconnue: {missing_handling}")
        
        # Filtrage des valeurs aberrantes
        if self.cleaning_rules.get('remove_outliers', False):
            method = self.cleaning_rules.get('outlier_method', 'zscore')
            threshold = self.cleaning_rules.get('outlier_threshold', 3)
            
            if method == 'zscore':
                # Suppression des valeurs aberrantes basée sur le Z-score
                numeric_cols = cleaned_data.select_dtypes(include=[np.number]).columns
                original_len = len(cleaned_data)
                
                for col in numeric_cols:
                    mean = cleaned_data[col].mean()
                    std = cleaned_data[col].std()
                    if std > 0:  # Éviter division par zéro
                        z_scores = (cleaned_data[col] - mean) / std
                        cleaned_data = cleaned_data[(z_scores.abs() <= threshold)]
                
                outliers_removed = original_len - len(cleaned_data)
                if outliers_removed > 0:
                    logger.info(f"Suppression de {outliers_removed} valeurs aberrantes (Z-score)")
            
            elif method == 'iqr':
                # Suppression des valeurs aberrantes basée sur l'IQR
                numeric_cols = cleaned_data.select_dtypes(include=[np.number]).columns
                original_len = len(cleaned_data)
                
                for col in numeric_cols:
                    Q1 = cleaned_data[col].quantile(0.25)
                    Q3 = cleaned_data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    cleaned_data = cleaned_data[(cleaned_data[col] >= lower_bound) & 
                                             (cleaned_data[col] <= upper_bound)]
                
                outliers_removed = original_len - len(cleaned_data)
                if outliers_removed > 0:
                    logger.info(f"Suppression de {outliers_removed} valeurs aberrantes (IQR)")
        
        # Suppression des colonnes avec trop de valeurs manquantes
        if 'drop_sparse_columns' in self.cleaning_rules:
            threshold = self.cleaning_rules['drop_sparse_columns']
            if 0 < threshold < 1:
                original_cols = cleaned_data.columns.tolist()
                min_count = int(threshold * len(cleaned_data))
                cleaned_data = cleaned_data.dropna(axis=1, thresh=min_count)
                dropped_cols = set(original_cols) - set(cleaned_data.columns.tolist())
                if dropped_cols:
                    logger.info(f"Suppression de {len(dropped_cols)} colonnes avec trop de valeurs manquantes: {', '.join(dropped_cols)}")
        
        return cleaned_data
    
    def transform_data(self, data):
        """
        Applique des transformations aux données.
        
        Args:
            data (pd.DataFrame): Les données à transformer
            
        Returns:
            pd.DataFrame: Les données transformées
        """
        if not isinstance(data, pd.DataFrame):
            logger.warning("Les données doivent être un DataFrame pandas")
            return data
        
        transformed_data = data.copy()
        
        # Normalisation / Standardisation
        normalization = self.transformation_rules.get('normalization')
        if normalization:
            numeric_cols = transformed_data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                logger.warning("Aucune colonne numérique trouvée pour la normalisation")
            else:
                logger.info(f"Application de la normalisation '{normalization}' aux colonnes numériques")
                
                if normalization == 'standard':
                    # Standardisation (moyenne=0, écart-type=1)
                    transformed_data[numeric_cols] = self.standard_scaler.fit_transform(transformed_data[numeric_cols])
                
                elif normalization == 'minmax':
                    # Normalisation Min-Max (plage [0,1])
                    transformed_data[numeric_cols] = self.minmax_scaler.fit_transform(transformed_data[numeric_cols])
                
                elif normalization == 'log':
                    # Transformation logarithmique
                    for col in numeric_cols:
                        # Ajouter un petit offset pour éviter log(0)
                        min_val = transformed_data[col].min()
                        offset = 1 if min_val >= 0 else abs(min_val) + 1
                        transformed_data[col] = np.log(transformed_data[col] + offset)
                
                else:
                    logger.warning(f"Méthode de normalisation non reconnue: {normalization}")
        
        # Traitement de texte basique
        if self.transformation_rules.get('text_processing', False):
            text_cols = transformed_data.select_dtypes(include=['object']).columns.tolist()
            
            if text_cols:
                logger.info(f"Application du traitement de texte à {len(text_cols)} colonnes")
                
                for col in text_cols:
                    # Convertir en minuscules
                    transformed_data[col] = transformed_data[col].astype(str).str.lower()
                    
                    # Supprimer la ponctuation et les caractères spéciaux
                    transformed_data[col] = transformed_data[col].apply(
                        lambda x: re.sub(r'[^\w\s]', '', str(x))
                    )
                    
                    # Supprimer les espaces multiples
                    transformed_data[col] = transformed_data[col].apply(
                        lambda x: re.sub(r'\s+', ' ', str(x)).strip()
                    )
        
        # One-hot encoding pour les variables catégorielles
        if self.transformation_rules.get('one_hot_encoding', False):
            categorical_cols = self.transformation_rules.get('categorical_columns', [])
            
            # Si aucune colonne spécifiée, détecter automatiquement
            if not categorical_cols:
                categorical_cols = transformed_data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if categorical_cols:
                logger.info(f"Application du one-hot encoding à {len(categorical_cols)} colonnes catégorielles")
                
                # Créer des variables indicatrices pour les colonnes catégorielles
                transformed_data = pd.get_dummies(
                    transformed_data, 
                    columns=categorical_cols,
                    drop_first=self.transformation_rules.get('drop_first', False)
                )
        
        # Création de caractéristiques temporelles
        if self.transformation_rules.get('date_features', False):
            date_cols = self.transformation_rules.get('date_columns', [])
            
            for col in date_cols:
                if col in transformed_data.columns:
                    try:
                        # Convertir en datetime si ce n'est pas déjà fait
                        transformed_data[col] = pd.to_datetime(transformed_data[col])
                        
                        # Extraire les composantes de date
                        transformed_data[f'{col}_year'] = transformed_data[col].dt.year
                        transformed_data[f'{col}_month'] = transformed_data[col].dt.month
                        transformed_data[f'{col}_day'] = transformed_data[col].dt.day
                        transformed_data[f'{col}_dayofweek'] = transformed_data[col].dt.dayofweek
                        
                        # Options additionnelles
                        if self.transformation_rules.get('time_features', False):
                            transformed_data[f'{col}_hour'] = transformed_data[col].dt.hour
                            transformed_data[f'{col}_minute'] = transformed_data[col].dt.minute
                        
                        logger.info(f"Création de caractéristiques temporelles pour la colonne {col}")
                    except Exception as e:
                        logger.warning(f"Erreur lors de la création de caractéristiques temporelles pour {col}: {str(e)}")
        
        return transformed_data
    
    def prepare_for_model(self, data):
        """
        Prépare les données pour l'entrée du modèle en appliquant
        nettoyage et transformations.
        
        Args:
            data (pd.DataFrame): Les données brutes
            
        Returns:
            pd.DataFrame: Les données préparées pour le modèle
        """
        logger.info("Préparation des données pour le modèle...")
        
        # Nettoyage des données
        cleaned_data = self.clean_data(data)
        
        # Transformation des données
        prepared_data = self.transform_data(cleaned_data)
        
        # Vérifier l'intégrité des données préparées
        if prepared_data is None or len(prepared_data) == 0:
            logger.warning("Les données préparées sont vides après traitement")
        else:
            logger.info(f"Données préparées avec succès: {len(prepared_data)} enregistrements, {len(prepared_data.columns)} caractéristiques")
        
        return prepared_data

# Exemple d'utilisation simple pour les tests
if __name__ == "__main__":
    # Créer un petit DataFrame de test
    test_data = pd.DataFrame({
        'A': [1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10],
        'B': [10, 20, 30, np.nan, 50, 60, 70, 80, 90, 100],
        'C': ['cat', 'dog', 'bird', 'fish', 'cat', 'dog', 'bird', 'fish', 'cat', 'dog'],
        'D': pd.date_range(start='2023-01-01', periods=10)
    })
    
    # Configurer les règles de nettoyage et transformation
    cleaning_rules = {
        'remove_duplicates': True,
        'handle_missing': 'mean',
        'remove_outliers': True,
        'outlier_method': 'zscore',
        'outlier_threshold': 2
    }
    
    transformation_rules = {
        'normalization': 'standard',
        'one_hot_encoding': True,
        'date_features': True,
        'date_columns': ['D']
    }
    
    # Créer et utiliser le processeur de données
    processor = DataProcessor(cleaning_rules, transformation_rules)
    prepared_data = processor.prepare_for_model(test_data)
    
    print("Données originales:")
    print(test_data.head())
    print("\nDonnées préparées:")
    print(prepared_data.head())
    print(f"\nColonnes des données préparées: {prepared_data.columns.tolist()}")