#!/usr/bin/env python3
"""
Flask server with OpenAI API integration.
Provides endpoints for chat completion and text analysis.
"""

import os
import json
import csv
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from openai_utils import chat_completion, analyze_sentiment, summarize_text
import logging

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
                "description": "Generate a response using OpenAI's chat completion"
            },
            {
                "path": "/api/analyze/sentiment",
                "method": "POST",
                "description": "Analyze the sentiment of a given text"
            },
            {
                "path": "/api/analyze/costs",
                "method": "GET",
                "description": "Analyze cost data from the CSV file"
            }
        ]
    })

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """
    Chat completion endpoint.
    
    Expects JSON with:
    - prompt: The user's message or question
    - model: (Optional) The model to use, defaults to gpt-4o
    """
    try:
        data = request.json
        
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' field in request body"}), 400
        
        prompt = data.get('prompt')
        model = data.get('model', 'gpt-4o')
        
        logger.info(f"Processing chat request with model: {model}")
        response = chat_completion(prompt, model)
        
        return jsonify({
            "response": response,
            "model": model,
            "mode": "simulation" if SIMULATION_MODE else "api"
        })
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/sentiment', methods=['POST'])
def handle_sentiment():
    """
    Sentiment analysis endpoint.
    
    Expects JSON with:
    - text: The text to analyze
    """
    try:
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field in request body"}), 400
        
        text = data.get('text')
        
        logger.info("Processing sentiment analysis request")
        result = analyze_sentiment(text)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing sentiment analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/costs', methods=['GET'])
def handle_cost_analysis():
    """
    Cost analysis endpoint.
    Reads and analyzes the cost CSV file.
    
    Query parameters:
    - period: Optional, 'day', 'week', or 'month'. Defaults to 'month'
    """
    try:
        period = request.args.get('period', 'month')
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
                "error": f"Failed to read cost data: {str(e)}",
                "message": "Échec de la lecture des données de coûts"
            }), 500
            
        # Convert date strings to datetime objects
        df['date'] = pd.to_datetime(df['date'])
        
        # Basic analysis
        total_tokens = df['tokens'].sum()
        total_cost = df['cost_usd'].sum()
        days_count = (df['date'].max() - df['date'].min()).days + 1
        avg_cost_per_day = total_cost / days_count
        
        # Detailed analysis based on the requested period
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
            
        # Prepare and return the result
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
            "period_data": period_data
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing cost analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def handle_summarize():
    """
    Text summarization endpoint.
    
    Expects JSON with:
    - text: The text to summarize
    """
    try:
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field in request body"}), 400
        
        text = data.get('text')
        
        logger.info("Processing text summarization request")
        result = summarize_text(text)
        
        return jsonify({
            "summary": result,
            "mode": "simulation" if SIMULATION_MODE else "api"
        })
    
    except Exception as e:
        logger.error(f"Error processing text summarization: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask application
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    logger.info(f"Server running on http://0.0.0.0:{port}")
