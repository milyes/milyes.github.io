#!/usr/bin/env node
/**
 * Express server with OpenAI API integration.
 * Provides endpoints for chat completion and text analysis.
 * With enhanced security and input validation.
 */

const express = require('express');
const { chatCompletion, analyzeSentiment, summarizeText } = require('./openai_utils');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Create Express application
const app = express();
app.use(express.json({
  limit: '1mb', // Limit size of JSON payloads
  verify: (req, res, buf) => {
    req.rawBody = buf; // Save raw body for potential signature verification
  }
}));

// Check if OpenAI API key is set
const SIMULATION_MODE = !process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY === '';
if (SIMULATION_MODE) {
  console.warn("OPENAI_API_KEY is not set. Running in simulation mode.");
}

// Security settings
const API_REQUESTS = {}; // Store for rate limiting {ip: { count, resetTime }}
const MAX_REQUESTS = 60; // Maximum requests per minute
const WINDOW_RESET_TIME = 60 * 1000; // Window in milliseconds for rate limiting

// Security middleware for rate limiting
function rateLimitMiddleware(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  
  // Initialize or reset rate limiting for this IP if needed
  if (!API_REQUESTS[ip] || now > API_REQUESTS[ip].resetTime) {
    API_REQUESTS[ip] = {
      count: 0,
      resetTime: now + WINDOW_RESET_TIME
    };
  }
  
  // Check if rate limit is exceeded
  if (API_REQUESTS[ip].count >= MAX_REQUESTS) {
    console.warn(`Rate limit exceeded for IP: ${ip}`);
    return res.status(429).json({
      error: "Trop de requêtes. Veuillez réessayer plus tard."
    });
  }
  
  // Increment request count
  API_REQUESTS[ip].count++;
  next();
}

// Apply rate limiting to all routes
app.use(rateLimitMiddleware);

// Input validation helpers
function isValidText(text) {
  return text && typeof text === 'string' && text.length >= 1 && text.length <= 10000;
}

function isValidModel(model) {
  const validModels = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"];
  return validModels.includes(model);
}

// Security middleware to sanitize inputs
function sanitizeInput(text) {
  if (!text) return '';
  // Remove potentially dangerous characters while preserving normal text
  return text.replace(/[^\w\s.,?!;:()\[\]{}'"«»\-]/g, '');
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
    
    // Validate required fields
    if (!prompt) {
      return res.status(400).json({ 
        error: "Le champ 'prompt' est requis dans le corps de la requête" 
      });
    }
    
    // Validate input format and length
    if (!isValidText(prompt)) {
      return res.status(400).json({ 
        error: "Le format ou la longueur du prompt est invalide"
      });
    }
    
    // Validate model
    if (!isValidModel(model)) {
      return res.status(400).json({ 
        error: `Modèle '${model}' non supporté. Utilisez l'un des modèles: gpt-4o, gpt-4, gpt-3.5-turbo`
      });
    }
    
    // Sanitize input
    const sanitizedPrompt = sanitizeInput(prompt);
    
    console.log(`Processing chat request with model: ${model}`);
    const response = await chatCompletion(sanitizedPrompt, model);
    
    // Generate request hash for traceability
    const requestId = crypto.createHash('md5')
      .update(sanitizedPrompt)
      .digest('hex')
      .substring(0, 8);
    
    console.log(`Successfully processed chat request with ${sanitizedPrompt.length} characters`);
    
    res.json({
      response,
      model,
      mode: SIMULATION_MODE ? "simulation" : "api",
      timestamp: new Date().toISOString(),
      request_id: requestId
    });
  } catch (error) {
    console.error(`Error processing chat request: ${error.message}`);
    res.status(500).json({ 
      error: "Une erreur est survenue lors du traitement de votre demande",
      detail: process.env.NODE_ENV === 'development' ? error.message : "Contactez l'administrateur pour plus d'informations"
    });
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
    
    // Validate required fields
    if (!text) {
      return res.status(400).json({ 
        error: "Le champ 'text' est requis dans le corps de la requête" 
      });
    }
    
    // Validate input format and length
    if (!isValidText(text)) {
      return res.status(400).json({ 
        error: "Le format ou la longueur du texte est invalide"
      });
    }
    
    // Sanitize input
    const sanitizedText = sanitizeInput(text);
    
    console.log("Processing sentiment analysis request");
    const result = await analyzeSentiment(sanitizedText);
    
    // Generate request hash for traceability
    const requestId = crypto.createHash('md5')
      .update(sanitizedText)
      .digest('hex')
      .substring(0, 8);
    
    console.log(`Successfully processed sentiment analysis with ${sanitizedText.length} characters`);
    
    // Add additional metadata to the result
    result.mode = SIMULATION_MODE ? "simulation" : "api";
    result.timestamp = new Date().toISOString();
    result.request_id = requestId;
    
    res.json(result);
  } catch (error) {
    console.error(`Error processing sentiment analysis: ${error.message}`);
    res.status(500).json({ 
      error: "Une erreur est survenue lors de l'analyse de sentiment",
      detail: process.env.NODE_ENV === 'development' ? error.message : "Contactez l'administrateur pour plus d'informations"
    });
  }
});

/**
 * Cost analysis endpoint.
 * Reads and analyzes the cost CSV file.
 * 
 * Query parameters:
 * - period: Optional, 'day', 'week', or 'month'. Defaults to 'month'
 */
app.get('/api/analyze/costs', (req, res) => {
  try {
    // Validate and sanitize period parameter
    const period = req.query.period || 'month';
    const validPeriods = ['day', 'week', 'month'];
    
    if (!validPeriods.includes(period)) {
      console.warn(`Invalid period requested: ${period}`);
      return res.status(400).json({
        error: `Période invalide: ${period}`,
        message: `Les périodes valides sont: ${validPeriods.join(', ')}`
      });
    }
    
    console.log(`Processing cost analysis with period: ${period}`);
    
    const csvFilePath = path.join(__dirname, '..', 'attached_assets', 'cost_2025-01-30_2025-03-01.csv');
    
    // Check if CSV file exists
    if (!fs.existsSync(csvFilePath)) {
      console.warn(`Cost CSV file not found at ${csvFilePath}`);
      return res.status(404).json({
        error: "Fichier de données introuvable",
        message: "Le fichier de données de coûts n'a pas été trouvé"
      });
    }
    
    try {
      // Read the CSV file
      const csvData = fs.readFileSync(csvFilePath, 'utf8');
      const lines = csvData.trim().split('\n');
      const headers = lines[0].split(',');
      
      // Verify required columns exist
      const requiredColumns = ['date', 'tokens', 'cost_usd'];
      const missingColumns = requiredColumns.filter(col => !headers.includes(col));
      
      if (missingColumns.length > 0) {
        return res.status(500).json({
          error: `Format de données invalide: colonnes manquantes: ${missingColumns.join(', ')}`,
          message: "Le fichier CSV ne contient pas les données requises"
        });
      }
      
      // Parse the CSV data with improved error handling
      const data = [];
      for (let i = 1; i < lines.length; i++) {
        try {
          const values = lines[i].split(',');
          
          // Skip if line doesn't have enough values
          if (values.length < headers.length) {
            console.warn(`Skipping line ${i+1}: insufficient values`);
            continue;
          }
          
          const entry = {};
          
          headers.forEach((header, index) => {
            if (header === 'date') {
              // Validate date format
              const dateStr = values[index];
              if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
                throw new Error(`Invalid date format on line ${i+1}: ${dateStr}`);
              }
              entry[header] = dateStr;
            } else if (header === 'tokens') {
              const tokens = parseInt(values[index], 10);
              if (isNaN(tokens)) {
                throw new Error(`Invalid token value on line ${i+1}: ${values[index]}`);
              }
              entry[header] = tokens;
            } else if (header === 'cost_usd') {
              const cost = parseFloat(values[index]);
              if (isNaN(cost)) {
                throw new Error(`Invalid cost value on line ${i+1}: ${values[index]}`);
              }
              entry[header] = cost;
            } else {
              entry[header] = values[index];
            }
          });
          
          data.push(entry);
        } catch (lineError) {
          console.error(`Error parsing line ${i+1}: ${lineError.message}`);
          // Continue with next line instead of failing completely
        }
      }
      
      console.log(`Successfully read cost data with ${data.length} records`);
      
      if (data.length === 0) {
        return res.status(500).json({
          error: "Aucune donnée valide trouvée",
          message: "Le fichier CSV ne contient aucune donnée valide"
        });
      }
      
      // Basic analysis with error handling
      try {
        const totalTokens = data.reduce((sum, item) => sum + item.tokens, 0);
        const totalCost = data.reduce((sum, item) => sum + item.cost_usd, 0);
        
        // Get date range
        const dates = data.map(item => new Date(item.date));
        const startDate = new Date(Math.min(...dates));
        const endDate = new Date(Math.max(...dates));
        const daysCount = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
        const avgCostPerDay = totalCost / daysCount;
        
        // Detailed analysis based on the requested period
        let periodData = [];
        
        try {
          if (period === 'day') {
            // Group by day (already have daily data)
            periodData = data.map(item => ({
              date: item.date,
              tokens: item.tokens,
              cost_usd: item.cost_usd
            }));
          } else if (period === 'week') {
            // Group by week
            const weeklyData = {};
            
            data.forEach(item => {
              const date = new Date(item.date);
              const weekNumber = getWeekNumber(date);
              
              if (!weeklyData[weekNumber]) {
                weeklyData[weekNumber] = { week: weekNumber, tokens: 0, cost_usd: 0 };
              }
              
              weeklyData[weekNumber].tokens += item.tokens;
              weeklyData[weekNumber].cost_usd += item.cost_usd;
            });
            
            periodData = Object.values(weeklyData);
          } else {
            // Group by month (default)
            const monthlyData = {};
            
            data.forEach(item => {
              const monthKey = item.date.substring(0, 7); // Format: YYYY-MM
              
              if (!monthlyData[monthKey]) {
                monthlyData[monthKey] = { month: monthKey, tokens: 0, cost_usd: 0 };
              }
              
              monthlyData[monthKey].tokens += item.tokens;
              monthlyData[monthKey].cost_usd += item.cost_usd;
            });
            
            periodData = Object.values(monthlyData);
          }
        } catch (periodError) {
          console.error(`Error in period-specific analysis: ${periodError.message}`);
          return res.status(500).json({
            error: "Erreur lors de l'analyse par période",
            detail: process.env.NODE_ENV === 'development' ? periodError.message : null
          });
        }
        
        // Generate request ID for traceability
        const requestId = crypto.createHash('md5')
          .update(`${period}-${new Date().toISOString()}`)
          .digest('hex')
          .substring(0, 8);
        
        // Prepare and return the result with additional metadata
        const result = {
          summary: {
            total_tokens: totalTokens,
            total_cost_usd: parseFloat(totalCost.toFixed(3)),
            days_analyzed: daysCount,
            average_daily_cost_usd: parseFloat(avgCostPerDay.toFixed(4)),
            date_range: {
              start: formatDate(startDate),
              end: formatDate(endDate)
            }
          },
          period: period,
          period_data: periodData,
          timestamp: new Date().toISOString(),
          request_id: requestId
        };
        
        console.log(`Cost analysis completed successfully for period: ${period}`);
        return res.json(result);
      } catch (analysisError) {
        console.error(`Error calculating cost summaries: ${analysisError.message}`);
        return res.status(500).json({
          error: "Erreur lors du calcul des résumés de coûts",
          detail: process.env.NODE_ENV === 'development' ? analysisError.message : null
        });
      }
    } catch (fileError) {
      console.error(`Error reading CSV file: ${fileError.message}`);
      return res.status(500).json({
        error: "Échec de la lecture des données de coûts",
        message: "Le fichier de données est invalide ou corrompu",
        detail: process.env.NODE_ENV === 'development' ? fileError.message : null
      });
    }
  } catch (error) {
    console.error(`Error processing cost analysis: ${error.message}`);
    return res.status(500).json({
      error: "Une erreur est survenue lors de l'analyse des coûts",
      detail: process.env.NODE_ENV === 'development' ? error.message : "Contactez l'administrateur pour plus d'informations"
    });
  }
});

// Helper function to get week number
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// Helper function to format date as YYYY-MM-DD
function formatDate(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

// Start the server
const PORT = process.env.PORT || 8000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT} in ${SIMULATION_MODE ? "SIMULATION" : "API"} mode`);
});
