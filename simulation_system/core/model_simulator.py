#!/usr/bin/env python3
"""
Module définissant les classes pour la simulation des différents modèles d'IA.
"""

import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime
import logging
import hashlib
import re
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Import conditionnel d'OpenAI pour éviter les erreurs si la clé n'est pas configurée
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelSimulator:
    """Simule les comportements de différents modèles d'IA."""
    
    def __init__(self, model_type, parameters=None, simulation_mode=True):
        """
        Initialise un simulateur de modèle.
        
        Args:
            model_type (str): Type de modèle ('chatbot', 'sentiment_analysis', 'summarization', etc.)
            parameters (dict, optional): Paramètres spécifiques au modèle. Par défaut à None.
            simulation_mode (bool, optional): Si True, simule les prédictions. Par défaut à True.
        """
        self.model_type = model_type
        self.parameters = parameters or {}
        self.simulation_mode = simulation_mode
        
        # Vérification de la disponibilité de l'API OpenAI si on n'est pas en mode simulation
        if not self.simulation_mode:
            if not OPENAI_AVAILABLE:
                logger.warning("Module OpenAI non disponible, passage en mode simulation")
                self.simulation_mode = True
            elif not os.environ.get("OPENAI_API_KEY"):
                logger.warning("Clé API OpenAI non configurée, passage en mode simulation")
                self.simulation_mode = True
            else:
                try:
                    self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                    logger.info("Client OpenAI initialisé avec succès")
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation du client OpenAI: {str(e)}")
                    self.simulation_mode = True
        
        logger.info(f"Simulateur de modèle '{model_type}' initialisé en mode {'simulation' if self.simulation_mode else 'API'}")
    
    def predict(self, input_data):
        """
        Génère des prédictions, réelles ou simulées selon le mode.
        
        Args:
            input_data: Les données d'entrée pour la prédiction
                - Pour chatbot: texte de la question
                - Pour sentiment_analysis: texte à analyser
                - Pour summarization: texte à résumer
                - Pour d'autres modèles: DataFrame avec les caractéristiques
        
        Returns:
            Prédictions générées par le modèle
        """
        if self.simulation_mode:
            return self._simulate_prediction(input_data)
        else:
            try:
                return self._real_prediction(input_data)
            except Exception as e:
                logger.error(f"Erreur lors de la prédiction réelle: {str(e)}")
                logger.warning("Fallback en mode simulation suite à une erreur")
                return self._simulate_prediction(input_data)
    
    def _simulate_prediction(self, input_data):
        """
        Génère des prédictions simulées basées sur des règles ou patterns.
        
        Args:
            input_data: Les données d'entrée pour la prédiction
        
        Returns:
            Prédictions simulées
        """
        # Générer un identifiant de requête pour la traçabilité
        request_id = hashlib.md5(str(input_data).encode()).hexdigest()[:8]
        timestamp = datetime.now().isoformat()
        
        # Logique de simulation selon le type de modèle
        if self.model_type == "chatbot":
            return self._simulate_chatbot(input_data, request_id, timestamp)
        
        elif self.model_type == "sentiment_analysis":
            return self._simulate_sentiment_analysis(input_data, request_id, timestamp)
        
        elif self.model_type == "summarization":
            return self._simulate_summarization(input_data, request_id, timestamp)
        
        elif self.model_type == "classification":
            return self._simulate_classification(input_data, request_id, timestamp)
        
        elif self.model_type == "regression":
            return self._simulate_regression(input_data, request_id, timestamp)
        
        else:
            logger.warning(f"Type de modèle inconnu: {self.model_type}")
            return {
                "error": f"Type de modèle non supporté: {self.model_type}",
                "request_id": request_id,
                "timestamp": timestamp
            }
    
    def _simulate_chatbot(self, input_text, request_id, timestamp):
        """
        Simule une réponse de chatbot.
        
        Args:
            input_text (str): Texte de la question
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Réponse simulée du chatbot
        """
        # Réponses génériques basées sur des mots-clés
        responses = {
            "bonjour": "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
            "salut": "Salut ! En quoi puis-je vous être utile ?",
            "merci": "De rien ! N'hésitez pas si vous avez d'autres questions.",
            "au revoir": "Au revoir ! Bonne journée !",
            "help": "Je suis un assistant simulé. Je peux répondre à des questions simples.",
            "aide": "Je suis un assistant simulé. Je peux répondre à des questions simples."
        }
        
        # Réponse par défaut si aucun mot-clé n'est trouvé
        default_responses = [
            "Je suis en mode simulation. Pour obtenir des réponses plus précises, veuillez configurer une clé API OpenAI valide.",
            "Désolé, je ne peux pas répondre à cette question en mode simulation.",
            "En tant qu'assistant simulé, mes capacités sont limitées. Pourriez-vous essayer une question plus simple ?",
            "Je comprends votre question, mais je ne peux y répondre qu'en mode simulation pour le moment."
        ]
        
        # Recherche de mots-clés dans l'entrée
        input_lower = input_text.lower()
        for keyword, response in responses.items():
            if keyword in input_lower:
                return {
                    "response": response,
                    "model": "gpt-4o (simulation)",
                    "mode": "simulation",
                    "request_id": request_id,
                    "timestamp": timestamp
                }
        
        # Si aucun mot-clé n'est trouvé, retourner une réponse par défaut
        return {
            "response": random.choice(default_responses),
            "model": "gpt-4o (simulation)",
            "mode": "simulation",
            "request_id": request_id,
            "timestamp": timestamp
        }
    
    def _simulate_sentiment_analysis(self, input_text, request_id, timestamp):
        """
        Simule une analyse de sentiment.
        
        Args:
            input_text (str): Texte à analyser
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Résultat simulé de l'analyse de sentiment
        """
        # Mots-clés positifs et négatifs pour une analyse basique
        positive_words = ['bien', 'bon', 'super', 'excellent', 'fantastique', 'merveilleux', 
                          'génial', 'aime', 'adore', 'heureux', 'content', 'positif']
        negative_words = ['mauvais', 'terrible', 'horrible', 'affreux', 'nul', 'déteste', 
                          'hais', 'triste', 'malheureux', 'décevant', 'négatif']
        
        # Compter les occurrences de mots positifs et négatifs
        input_lower = input_text.lower()
        positive_count = sum(1 for word in positive_words if word in input_lower)
        negative_count = sum(1 for word in negative_words if word in input_lower)
        
        # Déterminer le sentiment global
        if positive_count > negative_count:
            rating = min(5, 3 + positive_count - negative_count)
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            rating = max(1, 3 - negative_count + positive_count)
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            # Sentiment neutre
            rating = 3
            confidence = 0.5
        
        return {
            "rating": rating,
            "confidence": confidence,
            "note": "Résultat généré par le mode simulation",
            "mode": "simulation",
            "request_id": request_id,
            "timestamp": timestamp
        }
    
    def _simulate_summarization(self, input_text, request_id, timestamp):
        """
        Simule un résumé de texte.
        
        Args:
            input_text (str): Texte à résumer
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Résultat simulé de la summarization
        """
        # Simplification basique: prendre les premières phrases + dernière phrase
        sentences = re.split(r'[.!?]+', input_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {
                "summary": "Texte vide ou invalide.",
                "original_length": 0,
                "summary_length": 0,
                "compression_ratio": 0,
                "mode": "simulation",
                "request_id": request_id,
                "timestamp": timestamp
            }
        
        # Sélectionner les premières phrases et la dernière
        num_sentences = min(2, len(sentences))
        selected_sentences = sentences[:num_sentences]
        
        if len(sentences) > num_sentences:
            selected_sentences.append(sentences[-1])
        
        # Assembler le résumé
        summary = ". ".join(selected_sentences)
        if not summary.endswith((".", "!", "?")):
            summary += "."
        
        # Ajouter une note de simulation
        summary += "\n\n(Résumé généré par le mode simulation)"
        
        return {
            "summary": summary,
            "original_length": len(input_text),
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / len(input_text), 2),
            "model": "gpt-4o (simulation)",
            "mode": "simulation",
            "request_id": request_id,
            "timestamp": timestamp
        }
    
    def _simulate_classification(self, input_data, request_id, timestamp):
        """
        Simule une classification.
        
        Args:
            input_data (pd.DataFrame): Données d'entrée avec caractéristiques
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Résultat simulé de la classification
        """
        if not isinstance(input_data, pd.DataFrame):
            return {
                "error": "Les données d'entrée doivent être un DataFrame pandas",
                "request_id": request_id,
                "timestamp": timestamp
            }
        
        # Récupérer les classes possibles des paramètres ou en définir par défaut
        classes = self.parameters.get('classes', ['A', 'B', 'C'])
        class_weights = self.parameters.get('class_weights', None)
        
        if class_weights is None:
            # Probabilités égales pour toutes les classes
            class_weights = [1/len(classes)] * len(classes)
        
        # Simuler les prédictions pour chaque ligne
        predictions = []
        probabilities = []
        
        for i in range(len(input_data)):
            # Générer un indice de classe basé sur les poids
            class_index = np.random.choice(len(classes), p=class_weights)
            predicted_class = classes[class_index]
            predictions.append(predicted_class)
            
            # Générer des probabilités fictives pour chaque classe
            probs = np.random.dirichlet([2 if j == class_index else 1 for j in range(len(classes))])
            probabilities.append(dict(zip(classes, probs)))
        
        return {
            "predictions": predictions,
            "probabilities": probabilities,
            "model": "classification (simulation)",
            "mode": "simulation",
            "request_id": request_id,
            "timestamp": timestamp
        }
    
    def _simulate_regression(self, input_data, request_id, timestamp):
        """
        Simule une régression.
        
        Args:
            input_data (pd.DataFrame): Données d'entrée avec caractéristiques
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Résultat simulé de la régression
        """
        if not isinstance(input_data, pd.DataFrame):
            return {
                "error": "Les données d'entrée doivent être un DataFrame pandas",
                "request_id": request_id,
                "timestamp": timestamp
            }
        
        # Récupérer les paramètres de régression ou en définir par défaut
        base_value = self.parameters.get('base_value', 50)
        noise_level = self.parameters.get('noise_level', 10)
        
        # Simuler les prédictions pour chaque ligne
        predictions = []
        
        for i in range(len(input_data)):
            # Générer une prédiction basée sur la moyenne des valeurs numériques + bruit
            numeric_cols = input_data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                row_mean = input_data.iloc[i][numeric_cols].mean()
                # Utiliser la moyenne comme facteur d'influence
                prediction = base_value + row_mean * random.uniform(0.5, 1.5)
            else:
                prediction = base_value
            
            # Ajouter du bruit aléatoire
            prediction += random.uniform(-noise_level, noise_level)
            predictions.append(round(prediction, 2))
        
        return {
            "predictions": predictions,
            "model": "regression (simulation)",
            "mode": "simulation",
            "request_id": request_id,
            "timestamp": timestamp
        }
    
    def _real_prediction(self, input_data):
        """
        Utilise l'API réelle pour les prédictions.
        
        Args:
            input_data: Les données d'entrée pour la prédiction
        
        Returns:
            Prédictions réelles du modèle
        """
        if not hasattr(self, 'openai_client'):
            raise ValueError("Client OpenAI non initialisé. Impossible d'effectuer des prédictions réelles.")
        
        # Générer un identifiant de requête pour la traçabilité
        request_id = hashlib.md5(str(input_data).encode()).hexdigest()[:8]
        timestamp = datetime.now().isoformat()
        
        # Logique selon le type de modèle
        if self.model_type == "chatbot":
            return self._real_chatbot(input_data, request_id, timestamp)
        
        elif self.model_type == "sentiment_analysis":
            return self._real_sentiment_analysis(input_data, request_id, timestamp)
        
        elif self.model_type == "summarization":
            return self._real_summarization(input_data, request_id, timestamp)
        
        else:
            logger.warning(f"Type de modèle non supporté en mode API: {self.model_type}")
            return self._simulate_prediction(input_data)
    
    def _real_chatbot(self, input_text, request_id, timestamp):
        """
        Génère une réponse réelle de chatbot via l'API OpenAI.
        
        Args:
            input_text (str): Texte de la question
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Réponse du chatbot
        """
        model = self.parameters.get('model', 'gpt-4o')
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant utile et concis."},
                    {"role": "user", "content": input_text}
                ]
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": model,
                "mode": "api",
                "request_id": request_id,
                "timestamp": timestamp
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API OpenAI pour chatbot: {str(e)}")
            return self._simulate_chatbot(input_text, request_id, timestamp)
    
    def _real_sentiment_analysis(self, input_text, request_id, timestamp):
        """
        Effectue une analyse de sentiment réelle via l'API OpenAI.
        
        Args:
            input_text (str): Texte à analyser
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Résultat de l'analyse de sentiment
        """
        model = self.parameters.get('model', 'gpt-4o')
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Vous êtes un expert en analyse de sentiment. Analysez le sentiment du texte et "
                                  "fournissez une note de 1 à 5 étoiles et un score de confiance entre 0 et 1. "
                                  "Répondez avec un JSON au format: { 'rating': nombre, 'confidence': nombre }"
                    },
                    {"role": "user", "content": input_text}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Normaliser les valeurs
            rating = max(1, min(5, round(result.get('rating', 3))))
            confidence = max(0, min(1, result.get('confidence', 0.5)))
            
            return {
                "rating": rating,
                "confidence": confidence,
                "model": model,
                "mode": "api",
                "request_id": request_id,
                "timestamp": timestamp
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API OpenAI pour l'analyse de sentiment: {str(e)}")
            return self._simulate_sentiment_analysis(input_text, request_id, timestamp)
    
    def _real_summarization(self, input_text, request_id, timestamp):
        """
        Génère un résumé réel via l'API OpenAI.
        
        Args:
            input_text (str): Texte à résumer
            request_id (str): Identifiant de la requête
            timestamp (str): Horodatage
        
        Returns:
            dict: Résultat de la summarization
        """
        model = self.parameters.get('model', 'gpt-4o')
        max_tokens = self.parameters.get('max_tokens', 150)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Veuillez résumer le texte suivant de manière concise tout en préservant les points clés."
                    },
                    {"role": "user", "content": input_text}
                ],
                max_tokens=max_tokens
            )
            
            summary = response.choices[0].message.content
            
            return {
                "summary": summary,
                "original_length": len(input_text),
                "summary_length": len(summary),
                "compression_ratio": round(len(summary) / len(input_text), 2),
                "model": model,
                "mode": "api",
                "request_id": request_id,
                "timestamp": timestamp
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API OpenAI pour la summarization: {str(e)}")
            return self._simulate_summarization(input_text, request_id, timestamp)
    
    def evaluate_performance(self, predictions, actual_values=None):
        """
        Évalue la performance du modèle, simule si nécessaire.
        
        Args:
            predictions: Les prédictions générées par le modèle
            actual_values: Les valeurs réelles pour comparaison
            
        Returns:
            dict: Métriques de performance
        """
        # Si pas de valeurs réelles fournies, simuler l'évaluation
        if actual_values is None:
            return self._simulate_evaluation(predictions)
        
        # Évaluation réelle selon le type de modèle
        if self.model_type == "classification":
            return self._evaluate_classification(predictions, actual_values)
        
        elif self.model_type == "regression":
            return self._evaluate_regression(predictions, actual_values)
        
        elif self.model_type in ["chatbot", "sentiment_analysis", "summarization"]:
            return self._evaluate_text_model(predictions, actual_values)
        
        else:
            logger.warning(f"Évaluation non supportée pour le type de modèle: {self.model_type}")
            return self._simulate_evaluation(predictions)
    
    def _simulate_evaluation(self, predictions):
        """
        Simule une évaluation de performance.
        
        Args:
            predictions: Les prédictions générées par le modèle
            
        Returns:
            dict: Métriques de performance simulées
        """
        # Simuler des métriques de performance
        if self.model_type == "classification":
            return {
                "accuracy": round(random.uniform(0.7, 0.95), 3),
                "precision": round(random.uniform(0.7, 0.95), 3),
                "recall": round(random.uniform(0.7, 0.95), 3),
                "f1_score": round(random.uniform(0.7, 0.95), 3),
                "evaluation_mode": "simulation"
            }
        
        elif self.model_type == "regression":
            return {
                "mse": round(random.uniform(10, 100), 2),
                "rmse": round(random.uniform(3, 10), 2),
                "mae": round(random.uniform(2, 8), 2),
                "r2": round(random.uniform(0.6, 0.9), 3),
                "evaluation_mode": "simulation"
            }
        
        elif self.model_type in ["chatbot", "sentiment_analysis", "summarization"]:
            return {
                "relevance_score": round(random.uniform(0.7, 0.95), 3),
                "coherence_score": round(random.uniform(0.7, 0.95), 3),
                "quality_rating": round(random.uniform(3.5, 4.8), 1),
                "evaluation_mode": "simulation"
            }
        
        else:
            return {
                "performance_score": round(random.uniform(0.7, 0.95), 3),
                "confidence": round(random.uniform(0.6, 0.9), 3),
                "evaluation_mode": "simulation"
            }
    
    def _evaluate_classification(self, predictions, actual_values):
        """
        Évalue la performance d'un modèle de classification.
        
        Args:
            predictions: Les classes prédites
            actual_values: Les classes réelles
            
        Returns:
            dict: Métriques de performance
        """
        try:
            # Extraire les prédictions si elles sont dans un dictionnaire
            if isinstance(predictions, dict) and "predictions" in predictions:
                pred_values = predictions["predictions"]
            else:
                pred_values = predictions
            
            # Calculer les métriques
            accuracy = accuracy_score(actual_values, pred_values)
            
            # Pour les métriques suivantes, gérer le cas multiclasse
            average = 'binary' if len(np.unique(actual_values)) <= 2 else 'weighted'
            precision = precision_score(actual_values, pred_values, average=average, zero_division=0)
            recall = recall_score(actual_values, pred_values, average=average, zero_division=0)
            f1 = f1_score(actual_values, pred_values, average=average, zero_division=0)
            
            return {
                "accuracy": round(accuracy, 3),
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1_score": round(f1, 3),
                "evaluation_mode": "actual"
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de classification: {str(e)}")
            return self._simulate_evaluation(predictions)
    
    def _evaluate_regression(self, predictions, actual_values):
        """
        Évalue la performance d'un modèle de régression.
        
        Args:
            predictions: Les valeurs prédites
            actual_values: Les valeurs réelles
            
        Returns:
            dict: Métriques de performance
        """
        try:
            # Extraire les prédictions si elles sont dans un dictionnaire
            if isinstance(predictions, dict) and "predictions" in predictions:
                pred_values = predictions["predictions"]
            else:
                pred_values = predictions
            
            # Convertir en numpy arrays
            pred_values = np.array(pred_values)
            actual_values = np.array(actual_values)
            
            # Calculer les métriques
            mse = np.mean((pred_values - actual_values) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(pred_values - actual_values))
            
            # R² (coefficient de détermination)
            ss_total = np.sum((actual_values - np.mean(actual_values)) ** 2)
            ss_residual = np.sum((actual_values - pred_values) ** 2)
            r2 = 1 - (ss_residual / ss_total) if ss_total > 0 else 0
            
            return {
                "mse": round(mse, 2),
                "rmse": round(rmse, 2),
                "mae": round(mae, 2),
                "r2": round(r2, 3),
                "evaluation_mode": "actual"
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de régression: {str(e)}")
            return self._simulate_evaluation(predictions)
    
    def _evaluate_text_model(self, predictions, actual_values):
        """
        Évalue la performance d'un modèle textuel (chatbot, sentiment, summarization).
        
        Args:
            predictions: Les textes générés ou analyses
            actual_values: Les valeurs attendues
            
        Returns:
            dict: Métriques de performance
        """
        # Pour les modèles textuels, l'évaluation automatique est limitée
        # On pourrait utiliser des métriques comme BLEU, ROUGE, etc. pour la summarization
        # ou comparer des sentiments pour l'analyse de sentiment
        # Ici, on utilise une évaluation simulée mais plus réaliste
        
        logger.info("Évaluation automatique limitée pour les modèles textuels - simulation améliorée")
        
        # Si le modèle est une analyse de sentiment et que nous avons des valeurs réelles
        if self.model_type == "sentiment_analysis" and isinstance(predictions, dict) and "rating" in predictions:
            try:
                if isinstance(actual_values, list) and len(actual_values) == 1:
                    actual_rating = actual_values[0]
                elif isinstance(actual_values, (int, float)):
                    actual_rating = actual_values
                else:
                    raise ValueError("Format des valeurs réelles non supporté")
                
                pred_rating = predictions["rating"]
                
                # Calculer la différence entre les ratings
                rating_diff = abs(pred_rating - actual_rating)
                accuracy = max(0, 1 - (rating_diff / 4))  # Normaliser sur une échelle de 0 à 1
                
                return {
                    "rating_accuracy": round(accuracy, 3),
                    "rating_error": rating_diff,
                    "confidence": predictions.get("confidence", 0.5),
                    "evaluation_mode": "actual"
                }
            
            except Exception as e:
                logger.error(f"Erreur lors de l'évaluation du sentiment: {str(e)}")
        
        # Pour les autres cas, utiliser une simulation améliorée
        return {
            "relevance_score": round(random.uniform(0.7, 0.95), 3),
            "coherence_score": round(random.uniform(0.7, 0.95), 3),
            "quality_rating": round(random.uniform(3.5, 4.8), 1),
            "evaluation_mode": "simulation_enhanced"
        }

# Exemple d'utilisation simple pour les tests
if __name__ == "__main__":
    # Test du simulateur de chatbot
    chatbot = ModelSimulator("chatbot", simulation_mode=True)
    response = chatbot.predict("Bonjour, comment ça va?")
    print("Réponse du chatbot:")
    print(json.dumps(response, indent=2))
    
    # Test du simulateur d'analyse de sentiment
    sentiment_analyzer = ModelSimulator("sentiment_analysis", simulation_mode=True)
    sentiment = sentiment_analyzer.predict("J'adore ce produit, il est fantastique!")
    print("\nAnalyse de sentiment:")
    print(json.dumps(sentiment, indent=2))
    
    # Test du simulateur de résumé
    summarizer = ModelSimulator("summarization", simulation_mode=True)
    text_to_summarize = """
    L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer des systèmes capables de réaliser des tâches 
    qui nécessitent normalement l'intelligence humaine. Ces tâches comprennent l'apprentissage, le raisonnement, la résolution de problèmes, 
    la perception, la compréhension du langage et la prise de décision. L'IA peut être divisée en deux catégories principales: l'IA faible, 
    qui est conçue pour accomplir une tâche spécifique, et l'IA forte, qui possède les capacités cognitives d'un être humain. 
    Aujourd'hui, l'IA est utilisée dans de nombreux domaines, y compris la médecine, la finance, les transports et l'éducation.
    """
    summary = summarizer.predict(text_to_summarize)
    print("\nRésumé généré:")
    print(json.dumps(summary, indent=2))