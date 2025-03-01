#!/usr/bin/env python3
"""
Flask server with OpenAI API integration.
Provides endpoints for chat completion and text analysis.
"""

import os
import json
from flask import Flask, request, jsonify
from openai_utils import chat_completion, analyze_sentiment
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Check if OpenAI API key is set
if not os.environ.get("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY is not set. Please set it as an environment variable.")

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        "name": "OpenAI API Integration",
        "version": "1.0.0",
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
            "model": model
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

if __name__ == '__main__':
    # Run the Flask application
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    logger.info(f"Server running on http://0.0.0.0:{port}")
