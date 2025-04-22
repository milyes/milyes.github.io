#!/usr/bin/env python3
"""
Module définissant les classes pour la gestion des sorties du système de simulation.
"""

import os
import json
import csv
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OutputHandler:
    """Gère les sorties du système de simulation."""
    
    def __init__(self, output_format="json", destination=None):
        """
        Initialise un gestionnaire de sorties.
        
        Args:
            output_format (str, optional): Format de sortie ('json', 'csv', 'xlsx'). Par défaut à "json".
            destination (str, optional): Destination de sortie (chemin de fichier ou répertoire). Par défaut à None.
        """
        self.output_format = output_format.lower()
        self.destination = destination
        
        # Créer le répertoire de destination si nécessaire
        if self.destination and os.path.isdir(os.path.dirname(self.destination)):
            os.makedirs(os.path.dirname(self.destination), exist_ok=True)
    
    def format_output(self, data, metadata=None):
        """
        Formate les données selon le format spécifié.
        
        Args:
            data: Les données à formater (dict, list, DataFrame)
            metadata (dict, optional): Métadonnées additionnelles. Par défaut à None.
        
        Returns:
            Les données formatées selon le format spécifié
        """
        # Ajouter les métadonnées si fournies
        if metadata:
            if isinstance(data, dict):
                formatted_data = {**data, "metadata": metadata}
            elif isinstance(data, pd.DataFrame):
                # Convertir DataFrame en dict avec métadonnées
                formatted_data = {
                    "data": data.to_dict(orient="records"),
                    "metadata": metadata
                }
            else:
                # Pour les autres types, encapsuler dans un dict
                formatted_data = {
                    "data": data,
                    "metadata": metadata
                }
        else:
            formatted_data = data
        
        # Convertir au format spécifié
        if self.output_format == "json":
            try:
                # Gérer les types non sérialisables en JSON
                if isinstance(formatted_data, pd.DataFrame):
                    return formatted_data.to_json(orient="records", date_format="iso")
                else:
                    return json.dumps(formatted_data, default=self._json_serial)
            except Exception as e:
                logger.error(f"Erreur lors de la conversion en JSON: {str(e)}")
                return json.dumps({"error": "Erreur de formatage", "details": str(e)})
        
        elif self.output_format == "csv":
            try:
                if isinstance(formatted_data, pd.DataFrame):
                    return formatted_data.to_csv(index=False)
                elif isinstance(formatted_data, (dict, list)):
                    # Convertir en DataFrame pour le format CSV
                    df = pd.DataFrame(formatted_data)
                    return df.to_csv(index=False)
                else:
                    logger.warning(f"Type de données non supporté pour CSV: {type(formatted_data)}")
                    return str(formatted_data)
            except Exception as e:
                logger.error(f"Erreur lors de la conversion en CSV: {str(e)}")
                return f"Erreur de formatage: {str(e)}"
        
        elif self.output_format == "xlsx":
            # Pour XLSX, on ne peut pas retourner directement le contenu
            # On retourne un DataFrame qui sera sauvegardé dans save_output
            try:
                if isinstance(formatted_data, pd.DataFrame):
                    return formatted_data
                elif isinstance(formatted_data, (dict, list)):
                    return pd.DataFrame(formatted_data)
                else:
                    logger.warning(f"Type de données non supporté pour XLSX: {type(formatted_data)}")
                    return pd.DataFrame({"data": [str(formatted_data)]})
            except Exception as e:
                logger.error(f"Erreur lors de la conversion en DataFrame pour XLSX: {str(e)}")
                return pd.DataFrame({"error": [str(e)]})
        
        else:
            logger.warning(f"Format de sortie non supporté: {self.output_format}")
            return str(formatted_data)
    
    def _json_serial(self, obj):
        """
        Convertit les types non-sérialisables en JSON en chaînes de caractères.
        
        Args:
            obj: L'objet à sérialiser
        
        Returns:
            Une représentation sérialisable de l'objet
        """
        if isinstance(obj, (datetime, np.datetime64)):
            return obj.isoformat()
        elif isinstance(obj, np.int64):
            return int(obj)
        elif isinstance(obj, np.float64):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        raise TypeError(f"Type non sérialisable: {type(obj)}")
    
    def save_output(self, formatted_data):
        """
        Sauvegarde les données vers la destination.
        
        Args:
            formatted_data: Les données formatées à sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé ou message d'erreur
        """
        if not self.destination:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.destination = f"output_{timestamp}.{self.output_format}"
            logger.info(f"Aucune destination spécifiée, utilisation de: {self.destination}")
        
        try:
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(os.path.abspath(self.destination)), exist_ok=True)
            
            if self.output_format == "json":
                if isinstance(formatted_data, str):
                    # Déjà formaté en JSON
                    with open(self.destination, 'w', encoding='utf-8') as f:
                        f.write(formatted_data)
                else:
                    # Objet Python
                    with open(self.destination, 'w', encoding='utf-8') as f:
                        json.dump(formatted_data, f, default=self._json_serial, indent=2)
            
            elif self.output_format == "csv":
                if isinstance(formatted_data, str):
                    # Déjà formaté en CSV
                    with open(self.destination, 'w', encoding='utf-8') as f:
                        f.write(formatted_data)
                elif isinstance(formatted_data, pd.DataFrame):
                    formatted_data.to_csv(self.destination, index=False)
                else:
                    # Convertir en DataFrame
                    pd.DataFrame(formatted_data).to_csv(self.destination, index=False)
            
            elif self.output_format == "xlsx":
                if isinstance(formatted_data, pd.DataFrame):
                    formatted_data.to_excel(self.destination, index=False)
                else:
                    # Convertir en DataFrame
                    pd.DataFrame(formatted_data).to_excel(self.destination, index=False)
            
            else:
                # Format non supporté, sauvegarder comme texte
                with open(self.destination, 'w', encoding='utf-8') as f:
                    f.write(str(formatted_data))
            
            logger.info(f"Données sauvegardées avec succès: {self.destination}")
            return self.destination
        
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde des données: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def generate_report(self, simulation_results):
        """
        Génère un rapport de simulation avec métriques et visualisations.
        
        Args:
            simulation_results: Résultats de simulation (liste de dictionnaires)
            
        Returns:
            dict: Rapport généré avec chemin des visualisations
        """
        if not simulation_results:
            logger.warning("Aucun résultat de simulation à analyser")
            return {"error": "Aucun résultat de simulation disponible"}
        
        # Convertir en DataFrame pour faciliter l'analyse
        try:
            if isinstance(simulation_results, list):
                results_df = pd.DataFrame(simulation_results)
            elif isinstance(simulation_results, dict):
                # Si c'est un dictionnaire avec des listes de résultats
                if any(isinstance(v, list) for v in simulation_results.values()):
                    # Aplatir les données
                    flat_data = []
                    for key, value_list in simulation_results.items():
                        if isinstance(value_list, list):
                            for item in value_list:
                                if isinstance(item, dict):
                                    item["category"] = key
                                    flat_data.append(item)
                    results_df = pd.DataFrame(flat_data)
                else:
                    # Dictionnaire simple
                    results_df = pd.DataFrame([simulation_results])
            else:
                logger.warning(f"Format de résultats non supporté: {type(simulation_results)}")
                return {"error": f"Format de résultats non supporté: {type(simulation_results)}"}
        except Exception as e:
            logger.error(f"Erreur lors de la conversion des résultats en DataFrame: {str(e)}")
            return {"error": f"Erreur lors de la préparation des données: {str(e)}"}
        
        # Générer un répertoire pour les visualisations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = f"report_{timestamp}"
        os.makedirs(report_dir, exist_ok=True)
        
        # Générer un résumé statistique
        try:
            summary_stats = {}
            
            # Statistiques pour les colonnes numériques
            numeric_cols = results_df.select_dtypes(include=[np.number]).columns
            if not numeric_cols.empty:
                summary_stats["numeric"] = results_df[numeric_cols].describe().to_dict()
            
            # Comptage pour les colonnes catégorielles
            cat_cols = results_df.select_dtypes(include=["object", "category"]).columns
            if not cat_cols.empty:
                summary_stats["categorical"] = {
                    col: results_df[col].value_counts().to_dict() 
                    for col in cat_cols
                }
            
            # Sauvegarder le résumé
            with open(os.path.join(report_dir, "summary_stats.json"), 'w') as f:
                json.dump(summary_stats, f, default=self._json_serial, indent=2)
            
            logger.info(f"Résumé statistique généré: {os.path.join(report_dir, 'summary_stats.json')}")
        except Exception as e:
            logger.error(f"Erreur lors de la génération des statistiques: {str(e)}")
        
        # Générer des visualisations
        visualizations = []
        try:
            # Configurer le style des visualisations
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set(font_scale=1.2)
            
            # 1. Visualisations pour les colonnes numériques
            for col in numeric_cols:
                if len(results_df[col].unique()) > 1:  # Éviter les colonnes constantes
                    # Histogramme
                    plt.figure(figsize=(10, 6))
                    sns.histplot(results_df[col], kde=True)
                    plt.title(f"Distribution de {col}")
                    plt.tight_layout()
                    hist_path = os.path.join(report_dir, f"hist_{col}.png")
                    plt.savefig(hist_path)
                    plt.close()
                    visualizations.append({"type": "histogram", "column": col, "path": hist_path})
                    
                    # Boîte à moustaches
                    plt.figure(figsize=(10, 6))
                    sns.boxplot(y=results_df[col])
                    plt.title(f"Boîte à moustaches de {col}")
                    plt.tight_layout()
                    box_path = os.path.join(report_dir, f"boxplot_{col}.png")
                    plt.savefig(box_path)
                    plt.close()
                    visualizations.append({"type": "boxplot", "column": col, "path": box_path})
            
            # 2. Visualisations pour les colonnes catégorielles
            for col in cat_cols:
                if len(results_df[col].unique()) <= 10:  # Limiter aux colonnes avec peu de valeurs uniques
                    plt.figure(figsize=(10, 6))
                    value_counts = results_df[col].value_counts()
                    sns.barplot(x=value_counts.index, y=value_counts.values)
                    plt.title(f"Comptage des valeurs de {col}")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    bar_path = os.path.join(report_dir, f"barplot_{col}.png")
                    plt.savefig(bar_path)
                    plt.close()
                    visualizations.append({"type": "barplot", "column": col, "path": bar_path})
            
            # 3. Corrélations entre variables numériques
            if len(numeric_cols) > 1:
                plt.figure(figsize=(12, 10))
                corr = results_df[numeric_cols].corr()
                sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
                plt.title("Matrice de corrélation")
                plt.tight_layout()
                corr_path = os.path.join(report_dir, "correlation_matrix.png")
                plt.savefig(corr_path)
                plt.close()
                visualizations.append({"type": "correlation", "path": corr_path})
            
            # 4. Séries temporelles si une colonne de date est présente
            date_cols = [col for col in results_df.columns if "time" in col.lower() or "date" in col.lower()]
            for date_col in date_cols:
                try:
                    # Convertir en datetime
                    results_df[date_col] = pd.to_datetime(results_df[date_col])
                    
                    # Identifier une colonne numérique pour la série temporelle
                    if numeric_cols.empty:
                        continue
                    
                    value_col = numeric_cols[0]
                    plt.figure(figsize=(12, 6))
                    plt.plot(results_df[date_col], results_df[value_col], marker='o', linestyle='-')
                    plt.title(f"Évolution de {value_col} au fil du temps")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    time_path = os.path.join(report_dir, f"timeseries_{value_col}.png")
                    plt.savefig(time_path)
                    plt.close()
                    visualizations.append({"type": "timeseries", "column": value_col, "path": time_path})
                except Exception as e:
                    logger.warning(f"Impossible de créer une série temporelle pour {date_col}: {str(e)}")
            
            logger.info(f"Visualisations générées: {len(visualizations)}")
        except Exception as e:
            logger.error(f"Erreur lors de la génération des visualisations: {str(e)}")
        
        # Générer le rapport final
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_results": len(results_df),
                "data_columns": results_df.columns.tolist(),
                "stats_file": os.path.join(report_dir, "summary_stats.json") if "summary_stats" in locals() else None
            },
            "visualizations": visualizations,
            "report_directory": report_dir
        }
        
        # Sauvegarder le rapport
        report_path = os.path.join(report_dir, "report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, default=self._json_serial, indent=2)
        
        logger.info(f"Rapport généré avec succès: {report_path}")
        return report

# Exemple d'utilisation simple pour les tests
if __name__ == "__main__":
    # Créer des données de test
    test_data = {
        "predictions": [0.1, 0.2, 0.3, 0.4, 0.5],
        "actual_values": [0.15, 0.25, 0.35, 0.45, 0.55],
        "errors": [-0.05, -0.05, -0.05, -0.05, -0.05],
        "model_type": "regression",
        "timestamp": datetime.now().isoformat()
    }
    
    # Tester la sauvegarde en JSON
    json_handler = OutputHandler("json", "test_output.json")
    formatted_json = json_handler.format_output(test_data)
    json_handler.save_output(formatted_json)
    
    # Tester la sauvegarde en CSV
    csv_handler = OutputHandler("csv", "test_output.csv")
    formatted_csv = csv_handler.format_output(test_data)
    csv_handler.save_output(formatted_csv)
    
    # Tester la génération de rapport
    # Créer plusieurs résultats de simulation
    simulation_results = []
    for i in range(50):
        result = {
            "run_id": i,
            "accuracy": random.uniform(0.7, 0.95),
            "error_rate": random.uniform(0.05, 0.3),
            "processing_time": random.uniform(0.1, 2.0),
            "model_type": random.choice(["A", "B", "C"]),
            "timestamp": (datetime.now() + pd.Timedelta(days=i)).isoformat()
        }
        simulation_results.append(result)
    
    # Générer le rapport
    report_handler = OutputHandler("json")
    report = report_handler.generate_report(simulation_results)
    print(f"Rapport généré: {report['report_directory']}")