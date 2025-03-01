#!/usr/bin/env python3
"""
Utility functions for interacting with OpenAI API.
"""

import os
import json
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
DEFAULT_MODEL = "gpt-4o"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def chat_completion(prompt, model=DEFAULT_MODEL):
    """
    Generate a response using OpenAI's chat completion.
    
    Args:
        prompt (str): The user's message or question
        model (str, optional): The model to use. Defaults to DEFAULT_MODEL.
        
    Returns:
        str: The generated response
    """
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise Exception(f"Failed to get chat completion: {str(e)}")

def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: A dictionary with sentiment rating and confidence
    """
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
        raise Exception(f"Failed to analyze sentiment: {str(e)}")

def summarize_text(text):
    """
    Generate a concise summary of the input text.
    
    Args:
        text (str): The text to summarize
        
    Returns:
        str: The generated summary
    """
    try:
        prompt = f"Please summarize the following text concisely while maintaining key points:\n\n{text}"
        response = openai.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in text summarization: {str(e)}")
        raise Exception(f"Failed to summarize text: {str(e)}")
