#!/usr/bin/env python3
"""
Flask server with OpenAI API integration.
Provides endpoints for chat completion and text analysis.
"""

import os
import json
import csv
import pandas as pd
import time
import hashlib
import re
from datetime import datetime
from flask import Flask, request, jsonify, abort, Response
from openai_utils import chat_completion, analyze_sentiment, summarize_text
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Define paths
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "attached_assets")
COSTS_CSV_PATH = os.path.join(ASSETS_DIR, "cost_2025-01-30_2025-03-01.csv")

# Check if OpenAI API key is set
SIMULATION_MODE = not os.environ.get("OPENAI_API_KEY")
if SIMULATION_MODE:
    logger.warning("OPENAI_API_KEY is not set. Running in simulation mode.")
else:
    logger.info("OPENAI_API_KEY is set. Running in API mode.")

# Security settings
API_REQUESTS = {}  # Store for rate limiting {ip: [timestamps]}
MAX_REQUESTS = 60  # Maximum requests per minute
REQUEST_WINDOW = 60  # Window in seconds for rate limiting

# Simple security middleware for rate limiting
def rate_limit_middleware():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            # Initialize request tracking for this IP if not exists
            if ip not in API_REQUESTS:
                API_REQUESTS[ip] = []
            
            # Filter requests within the window
            API_REQUESTS[ip] = [t for t in API_REQUESTS[ip] if current_time - t < REQUEST_WINDOW]
            
            # Check if rate limit is exceeded
            if len(API_REQUESTS[ip]) >= MAX_REQUESTS:
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return jsonify({"error": "Trop de requêtes. Veuillez réessayer plus tard."}), 429
            
            # Add current request timestamp
            API_REQUESTS[ip].append(current_time)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Input validation helpers
def is_valid_text(text):
    """Validate text input - non-empty and reasonable length"""
    return text and isinstance(text, str) and 1 <= len(text) <= 10000

def is_valid_model(model):
    """Validate model name"""
    valid_models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
    return model in valid_models

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        "name": "OpenAI API Integration",
        "version": "1.0.0",
        "mode": "simulation" if SIMULATION_MODE else "api",
        "endpoints": [
            {
                "path": "/api/chat",
                "method": "POST",
                "description": "Générer une réponse à l'aide de la complétion de chat d'OpenAI"
            },
            {
                "path": "/api/analyze/sentiment",
                "method": "POST",
                "description": "Analyser le sentiment d'un texte donné"
            },
            {
                "path": "/api/analyze/costs",
                "method": "GET",
                "description": "Analyser les données de coût par période (jour, semaine, mois)"
            },
            {
                "path": "/api/summarize",
                "method": "POST",
                "description": "Générer un résumé concis du texte fourni"
            }
        ]
    })

@app.route('/api/chat', methods=['POST'])
@rate_limit_middleware()
def handle_chat():
    """
    Chat completion endpoint.
    
    Expects JSON with:
    - prompt: The user's message or question
    - model: (Optional) The model to use, defaults to gpt-4o
    """
    try:
        # Validate request has JSON body
        if not request.is_json:
            return jsonify({"error": "Le corps de la requête doit être au format JSON"}), 400
            
        data = request.json
        
        if not data or 'prompt' not in data:
            return jsonify({"error": "Le champ 'prompt' est requis dans le corps de la requête"}), 400
        
        prompt = data.get('prompt')
        model = data.get('model', 'gpt-4o')
        
        # Validate input
        if not is_valid_text(prompt):
            return jsonify({"error": "Le format ou la longueur du prompt est invalide"}), 400
            
        if not is_valid_model(model):
            return jsonify({"error": f"Modèle '{model}' non supporté. Utilisez l'un des modèles: gpt-4o, gpt-4, gpt-3.5-turbo"}), 400
        
        # Sanitize input - remove any potentially harmful characters
        prompt = re.sub(r'[^\w\s.,?!;:()\[\]{}\'"-]', '', prompt)
        
        logger.info(f"Processing chat request with model: {model}")
        response = chat_completion(prompt, model)
        
        # Log successful request
        logger.info(f"Successfully processed chat request with {len(prompt)} characters")
        
        return jsonify({
            "response": response,
            "model": model,
            "mode": "simulation" if SIMULATION_MODE else "api",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            "error": "Une erreur est survenue lors du traitement de votre demande",
            "detail": str(e) if app.debug else "Contactez l'administrateur pour plus d'informations"
        }), 500

@app.route('/api/analyze/sentiment', methods=['POST'])
@rate_limit_middleware()
def handle_sentiment():
    """
    Sentiment analysis endpoint.
    
    Expects JSON with:
    - text: The text to analyze
    """
    try:
        # Validate request has JSON body
        if not request.is_json:
            return jsonify({"error": "Le corps de la requête doit être au format JSON"}), 400
            
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({"error": "Le champ 'text' est requis dans le corps de la requête"}), 400
        
        text = data.get('text')
        
        # Validate input
        if not is_valid_text(text):
            return jsonify({"error": "Le format ou la longueur du texte est invalide"}), 400
            
        # Sanitize input - remove any potentially harmful characters
        text = re.sub(r'[^\w\s.,?!;:()\[\]{}\'"-]', '', text)
        
        logger.info("Processing sentiment analysis request")
        result = analyze_sentiment(text)
        
        # Add timestamp and request hash for traceability
        request_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        result.update({
            "mode": "simulation" if SIMULATION_MODE else "api",
            "timestamp": datetime.now().isoformat(),
            "request_id": request_hash
        })
        
        logger.info(f"Successfully processed sentiment analysis with {len(text)} characters")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing sentiment analysis: {str(e)}")
        return jsonify({
            "error": "Une erreur est survenue lors de l'analyse de sentiment",
            "detail": str(e) if app.debug else "Contactez l'administrateur pour plus d'informations"
        }), 500

@app.route('/api/analyze/costs', methods=['GET'])
@rate_limit_middleware()
def handle_cost_analysis():
    """
    Cost analysis endpoint.
    Reads and analyzes the cost CSV file.
    
    Query parameters:
    - period: Optional, 'day', 'week', or 'month'. Defaults to 'month'
    """
    try:
        # Validate and sanitize period parameter
        period = request.args.get('period', 'month')
        valid_periods = ['day', 'week', 'month']
        
        if period not in valid_periods:
            logger.warning(f"Invalid period requested: {period}")
            return jsonify({
                "error": f"Période invalide: {period}",
                "message": "Les périodes valides sont: " + ", ".join(valid_periods)
            }), 400
            
        logger.info(f"Processing cost analysis with period: {period}")
        
        # Check if CSV file exists
        if not os.path.exists(COSTS_CSV_PATH):
            logger.warning(f"Cost CSV file not found at {COSTS_CSV_PATH}")
            return jsonify({
                "error": "Cost data file not found",
                "message": "Le fichier de données de coûts n'a pas été trouvé"
            }), 404
        
        # Read the CSV file using pandas for easier data manipulation
        try:
            df = pd.read_csv(COSTS_CSV_PATH)
            logger.info(f"Successfully read cost data with {len(df)} records")
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            return jsonify({
                "error": "Échec de la lecture des données de coûts",
                "message": "Le fichier de données est invalide ou corrompu",
                "detail": str(e) if app.debug else None
            }), 500
            
        # Convert date strings to datetime objects
        try:
            df['date'] = pd.to_datetime(df['date'])
            
            # Verify required columns exist
            required_columns = ['date', 'tokens', 'cost_usd']
            for col in required_columns:
                if col not in df.columns:
                    return jsonify({
                        "error": f"Format de données invalide: colonne '{col}' manquante",
                        "message": "Le fichier CSV ne contient pas les données requises"
                    }), 500
        except Exception as e:
            logger.error(f"Error parsing dates in CSV: {str(e)}")
            return jsonify({
                "error": "Format de date invalide dans le fichier CSV",
                "detail": str(e) if app.debug else None
            }), 500
        
        # Basic analysis with error handling for unexpected data types
        try:
            total_tokens = df['tokens'].sum()
            total_cost = df['cost_usd'].sum()
            days_count = (df['date'].max() - df['date'].min()).days + 1
            avg_cost_per_day = total_cost / days_count
        except Exception as e:
            logger.error(f"Error calculating cost summaries: {str(e)}")
            return jsonify({
                "error": "Erreur lors du calcul des résumés de coûts",
                "detail": str(e) if app.debug else None
            }), 500
        
        # Detailed analysis based on the requested period
        try:
            if period == 'day':
                grouped = df.groupby('date').agg({
                    'tokens': 'sum',
                    'cost_usd': 'sum'
                }).reset_index()
                grouped['date'] = grouped['date'].dt.strftime('%Y-%m-%d')
                
                period_data = [
                    {
                        'date': row['date'],
                        'tokens': int(row['tokens']),
                        'cost_usd': float(row['cost_usd'])
                    }
                    for _, row in grouped.iterrows()
                ]
            elif period == 'week':
                df['week'] = df['date'].dt.isocalendar().week
                grouped = df.groupby('week').agg({
                    'tokens': 'sum',
                    'cost_usd': 'sum'
                }).reset_index()
                
                period_data = [
                    {
                        'week': int(row['week']),
                        'tokens': int(row['tokens']),
                        'cost_usd': float(row['cost_usd'])
                    }
                    for _, row in grouped.iterrows()
                ]
            else:  # month is default
                df['month'] = df['date'].dt.strftime('%Y-%m')
                grouped = df.groupby('month').agg({
                    'tokens': 'sum',
                    'cost_usd': 'sum'
                }).reset_index()
                
                period_data = [
                    {
                        'month': row['month'],
                        'tokens': int(row['tokens']),
                        'cost_usd': float(row['cost_usd'])
                    }
                    for _, row in grouped.iterrows()
                ]
        except Exception as e:
            logger.error(f"Error in period-specific analysis: {str(e)}")
            return jsonify({
                "error": "Erreur lors de l'analyse par période",
                "detail": str(e) if app.debug else None
            }), 500
            
        # Prepare and return the result with additional metadata
        result = {
            "summary": {
                "total_tokens": int(total_tokens),
                "total_cost_usd": float(total_cost),
                "days_analyzed": days_count,
                "average_daily_cost_usd": float(avg_cost_per_day),
                "date_range": {
                    "start": df['date'].min().strftime('%Y-%m-%d'),
                    "end": df['date'].max().strftime('%Y-%m-%d')
                }
            },
            "period": period,
            "period_data": period_data,
            "timestamp": datetime.now().isoformat(),
            "request_id": hashlib.md5(f"{period}-{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        }
        
        # Cache result for 5 minutes (no actual caching implementation here)
        logger.info(f"Cost analysis completed successfully for period: {period}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing cost analysis: {str(e)}")
        return jsonify({
            "error": "Une erreur est survenue lors de l'analyse des coûts",
            "detail": str(e) if app.debug else "Contactez l'administrateur pour plus d'informations"
        }), 500

@app.route('/api/summarize', methods=['POST'])
@rate_limit_middleware()
def handle_summarize():
    """
    Text summarization endpoint.
    
    Expects JSON with:
    - text: The text to summarize
    """
    try:
        # Validate request has JSON body
        if not request.is_json:
            return jsonify({"error": "Le corps de la requête doit être au format JSON"}), 400
            
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({"error": "Le champ 'text' est requis dans le corps de la requête"}), 400
        
        text = data.get('text')
        
        # Validate input
        if not is_valid_text(text):
            return jsonify({"error": "Le format ou la longueur du texte est invalide"}), 400
            
        # Sanitize input - remove any potentially harmful characters
        text = re.sub(r'[^\w\s.,?!;:()\[\]{}\'"-]', '', text)
        
        logger.info("Processing text summarization request")
        result = summarize_text(text)
        
        # Generate request hash for traceability
        request_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        
        logger.info(f"Successfully processed summarization with {len(text)} characters")
        
        return jsonify({
            "summary": result,
            "mode": "simulation" if SIMULATION_MODE else "api",
            "timestamp": datetime.now().isoformat(),
            "request_id": request_hash
        })
    
    except Exception as e:
        logger.error(f"Error processing text summarization: {str(e)}")
        return jsonify({
            "error": "Une erreur est survenue lors de la génération du résumé",
            "detail": str(e) if app.debug else "Contactez l'administrateur pour plus d'informations"
        }), 500

if __name__ == '__main__':
    # Run the Flask application
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    logger.info(f"Server running on http://0.0.0.0:{port}")
