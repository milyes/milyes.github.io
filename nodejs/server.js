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
 * 
 * Query parameters:
 * - period: Optional, 'day', 'week', or 'month'. Defaults to 'month'
 */
app.get('/api/analyze/costs', (req, res) => {
  try {
    const period = req.query.period || 'month';
    console.log(`Processing cost analysis with period: ${period}`);

    const csvFilePath = path.join(__dirname, '..', 'attached_assets', 'cost_2025-01-30_2025-03-01.csv');
    
    // Check if CSV file exists
    if (!fs.existsSync(csvFilePath)) {
      console.warn(`Cost CSV file not found at ${csvFilePath}`);
      return res.status(404).json({
        error: "Cost data file not found",
        message: "Le fichier de données de coûts n'a pas été trouvé"
      });
    }

    // Read the CSV file
    const csvData = fs.readFileSync(csvFilePath, 'utf8');
    const lines = csvData.trim().split('\n');
    const headers = lines[0].split(',');
    
    // Parse the CSV data
    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      const entry = {};
      
      headers.forEach((header, index) => {
        if (header === 'date') {
          entry[header] = values[index];
        } else if (header === 'tokens') {
          entry[header] = parseInt(values[index], 10);
        } else if (header === 'cost_usd') {
          entry[header] = parseFloat(values[index]);
        } else {
          entry[header] = values[index];
        }
      });
      
      data.push(entry);
    }
    
    console.log(`Successfully read cost data with ${data.length} records`);
    
    // Basic analysis
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
    
    // Prepare and return the result
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
      period_data: periodData
    };
    
    res.json(result);
  } catch (error) {
    console.error(`Error processing cost analysis: ${error.message}`);
    res.status(500).json({ error: error.message });
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
