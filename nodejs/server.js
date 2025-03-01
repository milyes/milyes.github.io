#!/usr/bin/env node
/**
 * Express server with OpenAI API integration.
 * Provides endpoints for chat completion and text analysis.
 */

const express = require('express');
const { chatCompletion, analyzeSentiment, summarizeText } = require('./openai_utils');
const fs = require('fs');
const path = require('path');

// Create Express application
const app = express();
app.use(express.json());

// Check if OpenAI API key is set
const SIMULATION_MODE = !process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY === '';
if (SIMULATION_MODE) {
  console.warn("OPENAI_API_KEY is not set. Running in simulation mode.");
}

// Root endpoint with API information
app.get('/', (req, res) => {
  res.json({
    name: "OpenAI API Integration",
    version: "1.0.0",
    mode: SIMULATION_MODE ? "simulation" : "api",
    endpoints: [
      {
        path: "/api/chat",
        method: "POST",
        description: "Generate a response using OpenAI's chat completion"
      },
      {
        path: "/api/analyze/sentiment",
        method: "POST",
        description: "Analyze the sentiment of a given text"
      },
      {
        path: "/api/analyze/costs",
        method: "GET",
        description: "Analyze cost data from the CSV file (soon)"
      }
    ]
  });
});

/**
 * Chat completion endpoint.
 * 
 * Expects JSON with:
 * - prompt: The user's message or question
 * - model: (Optional) The model to use, defaults to gpt-4o
 */
app.post('/api/chat', async (req, res) => {
  try {
    const { prompt, model = 'gpt-4o' } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: "Missing 'prompt' field in request body" });
    }
    
    console.log(`Processing chat request with model: ${model}`);
    const response = await chatCompletion(prompt, model);
    
    res.json({
      response,
      model,
      mode: SIMULATION_MODE ? "simulation" : "api"
    });
  } catch (error) {
    console.error(`Error processing chat request: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Sentiment analysis endpoint.
 * 
 * Expects JSON with:
 * - text: The text to analyze
 */
app.post('/api/analyze/sentiment', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: "Missing 'text' field in request body" });
    }
    
    console.log("Processing sentiment analysis request");
    const result = await analyzeSentiment(text);
    
    res.json(result);
  } catch (error) {
    console.error(`Error processing sentiment analysis: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Cost analysis endpoint.
 * Reads and analyzes the cost CSV file.
 */
app.get('/api/analyze/costs', (req, res) => {
  try {
    // For now, just return placeholder data
    res.json({
      message: "Cost analysis endpoint",
      note: "Cette fonctionnalité sera mise en œuvre dans une prochaine version",
      status: "in_development"
    });
  } catch (error) {
    console.error(`Error processing cost analysis: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// Start the server
const PORT = process.env.PORT || 8000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT} in ${SIMULATION_MODE ? "SIMULATION" : "API"} mode`);
});
