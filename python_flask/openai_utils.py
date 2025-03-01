#!/usr/bin/env python3
"""
Utility functions for interacting with OpenAI API.
"""

import os
import json
import logging
import random
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
DEFAULT_MODEL = "gpt-4o"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SIMULATION_MODE = OPENAI_API_KEY is None or OPENAI_API_KEY == ""

if not SIMULATION_MODE:
    try:
        openai = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {str(e)}")
        SIMULATION_MODE = True
        logger.warning("Falling back to simulation mode due to OpenAI client initialization error")

def chat_completion(prompt, model=DEFAULT_MODEL):
    """
    Generate a response using OpenAI's chat completion.
    
    Args:
        prompt (str): The user's message or question
        model (str, optional): The model to use. Defaults to DEFAULT_MODEL.
        
    Returns:
        str: The generated response
    """
    if SIMULATION_MODE:
        logger.info("Running in simulation mode - generating mock response")
        return simulate_chat_response(prompt)
    
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        return simulate_chat_response(prompt, error=True)

def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: A dictionary with sentiment rating and confidence
    """
    if SIMULATION_MODE:
        logger.info("Running in simulation mode - generating mock sentiment analysis")
        return simulate_sentiment_analysis(text)
    
    try:
        response = openai.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentiment analysis expert. "
                    + "Analyze the sentiment of the text and provide a rating "
                    + "from 1 to 5 stars and a confidence score between 0 and 1. "
                    + "Respond with JSON in this format: "
                    + "{'rating': number, 'confidence': number}",
                },
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "rating": max(1, min(5, round(result["rating"]))),
            "confidence": max(0, min(1, result["confidence"])),
        }
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return simulate_sentiment_analysis(text, error=True)

def summarize_text(text):
    """
    Generate a concise summary of the input text.
    
    Args:
        text (str): The text to summarize
        
    Returns:
        str: The generated summary
    """
    if SIMULATION_MODE:
        logger.info("Running in simulation mode - generating mock summary")
        return simulate_summary(text)
    
    try:
        prompt = f"Please summarize the following text concisely while maintaining key points:\n\n{text}"
        response = openai.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in text summarization: {str(e)}")
        return simulate_summary(text, error=True)

# Simulation functions for when API key is not available
def simulate_chat_response(prompt, error=False):
    """Generate a simulated response for demonstration purposes."""
    if error:
        return "Je ne peux pas répondre à votre question pour le moment. (Mode simulation - erreur OpenAI)"
    
    responses = [
        f"Ceci est une réponse simulée à: '{prompt}'. Je ne suis pas en train d'utiliser l'API OpenAI actuellement.",
        "Bonjour ! Je suis en mode simulation car aucune clé API OpenAI valide n'est configurée.",
        "Pour obtenir de vraies réponses, veuillez configurer une clé API OpenAI valide.",
        "Cette réponse est générée localement pour démontrer le fonctionnement de l'API sans connexion à OpenAI."
    ]
    return random.choice(responses)

def simulate_sentiment_analysis(text, error=False):
    """Generate simulated sentiment analysis results."""
    if error:
        return {
            "rating": 3,
            "confidence": 0.5,
            "note": "Résultat généré par le mode simulation - erreur OpenAI"
        }
    
    # Simple word-based sentiment analysis
    positive_words = ["bon", "bien", "super", "excellent", "content", "heureux", "aimer", "génial"]
    negative_words = ["mauvais", "horrible", "terrible", "déteste", "nul", "pire", "déçu"]
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        rating = min(5, 3 + pos_count - neg_count)
        confidence = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
    elif neg_count > pos_count:
        rating = max(1, 3 - (neg_count - pos_count))
        confidence = min(0.9, 0.5 + (neg_count - pos_count) * 0.1)
    else:
        rating = 3
        confidence = 0.5
    
    return {
        "rating": rating,
        "confidence": confidence,
        "note": "Résultat généré par le mode simulation"
    }

def simulate_summary(text, error=False):
    """Generate a simulated summary of the text."""
    if error:
        return "Impossible de générer un résumé. (Mode simulation - erreur OpenAI)"
    
    # Simple summarization - take first and last sentence
    sentences = text.split('.')
    if len(sentences) <= 2:
        return text
    
    summary = f"{sentences[0].strip()}... {sentences[-2].strip()}."
    return f"{summary}\n\n(Résumé généré par le mode simulation)"
