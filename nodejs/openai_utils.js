/**
 * Utility functions for interacting with OpenAI API.
 */

const OpenAI = require('openai');

// the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
// do not change this unless explicitly requested by the user
const DEFAULT_MODEL = "gpt-4o";

// Check if OpenAI API key is available
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
let SIMULATION_MODE = !OPENAI_API_KEY || OPENAI_API_KEY === '';

// Initialize OpenAI client if not in simulation mode
let openai;
if (!SIMULATION_MODE) {
  try {
    // Create the OpenAI client
    openai = new OpenAI({ apiKey: OPENAI_API_KEY });
    
    // Validate the API key with a minimal request
    const validateApiKey = async () => {
      try {
        const response = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: [{ role: "user", content: "test" }],
          max_tokens: 5
        });
        console.log("OpenAI API key validated successfully");
        return true;
      } catch (error) {
        console.error(`Error with OpenAI API key: ${error.message}`);
        SIMULATION_MODE = true;
        console.warn("Falling back to simulation mode due to invalid or unauthorized API key");
        return false;
      }
    };
    
    // Immediately execute the validation
    validateApiKey();
  } catch (error) {
    console.error(`Error initializing OpenAI client: ${error.message}`);
    console.warn("Falling back to simulation mode");
    SIMULATION_MODE = true;
  }
} else {
  console.warn("No OpenAI API key provided. Running in simulation mode.");
}

/**
 * Generate a response using OpenAI's chat completion.
 * 
 * @param {string} prompt - The user's message or question
 * @param {string} [model=DEFAULT_MODEL] - The model to use
 * @returns {Promise<string>} The generated response
 */
async function chatCompletion(prompt, model = DEFAULT_MODEL) {
  if (SIMULATION_MODE) {
    console.log("Running in simulation mode - generating mock response");
    return simulateChatResponse(prompt);
  }
  
  try {
    const response = await openai.chat.completions.create({
      model: model,
      messages: [{ role: "user", content: prompt }],
    });
    
    return response.choices[0].message.content;
  } catch (error) {
    console.error(`Error in chat completion: ${error.message}`);
    return simulateChatResponse(prompt, true);
  }
}

/**
 * Analyze the sentiment of a given text.
 * 
 * @param {string} text - The text to analyze
 * @returns {Promise<Object>} A dictionary with sentiment rating and confidence
 */
async function analyzeSentiment(text) {
  if (SIMULATION_MODE) {
    console.log("Running in simulation mode - generating mock sentiment analysis");
    return simulateSentimentAnalysis(text);
  }
  
  try {
    const response = await openai.chat.completions.create({
      model: DEFAULT_MODEL,
      messages: [
        {
          role: "system",
          content: "You are a sentiment analysis expert. " +
            "Analyze the sentiment of the text and provide a rating " +
            "from 1 to 5 stars and a confidence score between 0 and 1. " +
            "Respond with JSON in this format: " +
            "{'rating': number, 'confidence': number}",
        },
        { role: "user", content: text },
      ],
      response_format: { type: "json_object" },
    });
    
    const result = JSON.parse(response.choices[0].message.content);
    return {
      rating: Math.max(1, Math.min(5, Math.round(result.rating))),
      confidence: Math.max(0, Math.min(1, result.confidence)),
    };
  } catch (error) {
    console.error(`Error in sentiment analysis: ${error.message}`);
    return simulateSentimentAnalysis(text, true);
  }
}

/**
 * Generate a concise summary of the input text.
 * 
 * @param {string} text - The text to summarize
 * @returns {Promise<string>} The generated summary
 */
async function summarizeText(text) {
  if (SIMULATION_MODE) {
    console.log("Running in simulation mode - generating mock summary");
    return simulateSummary(text);
  }
  
  try {
    const prompt = `Please summarize the following text concisely while maintaining key points:\n\n${text}`;
    const response = await openai.chat.completions.create({
      model: DEFAULT_MODEL,
      messages: [{ role: "user", content: prompt }],
    });
    
    return response.choices[0].message.content;
  } catch (error) {
    console.error(`Error in text summarization: ${error.message}`);
    return simulateSummary(text, true);
  }
}

// Simulation functions for when API key is not available
/**
 * Generate a simulated response for demonstration purposes.
 * 
 * @param {string} prompt - The user's prompt
 * @param {boolean} error - Whether an error occurred
 * @returns {string} A simulated response
 */
function simulateChatResponse(prompt, error = false) {
  if (error) {
    return "Je ne peux pas répondre à votre question pour le moment. (Mode simulation - erreur OpenAI)";
  }
  
  const responses = [
    `Ceci est une réponse simulée à: '${prompt}'. Je ne suis pas en train d'utiliser l'API OpenAI actuellement.`,
    "Bonjour ! Je suis en mode simulation car aucune clé API OpenAI valide n'est configurée.",
    "Pour obtenir de vraies réponses, veuillez configurer une clé API OpenAI valide.",
    "Cette réponse est générée localement pour démontrer le fonctionnement de l'API sans connexion à OpenAI."
  ];
  
  return responses[Math.floor(Math.random() * responses.length)];
}

/**
 * Generate simulated sentiment analysis results.
 * 
 * @param {string} text - The text to analyze
 * @param {boolean} error - Whether an error occurred
 * @returns {Object} A simulated sentiment analysis result
 */
function simulateSentimentAnalysis(text, error = false) {
  if (error) {
    return {
      rating: 3,
      confidence: 0.5,
      note: "Résultat généré par le mode simulation - erreur OpenAI"
    };
  }
  
  // Simple word-based sentiment analysis
  const positiveWords = ["bon", "bien", "super", "excellent", "content", "heureux", "aimer", "génial"];
  const negativeWords = ["mauvais", "horrible", "terrible", "déteste", "nul", "pire", "déçu"];
  
  const textLower = text.toLowerCase();
  let posCount = 0;
  let negCount = 0;
  
  positiveWords.forEach(word => {
    if (textLower.includes(word)) posCount++;
  });
  
  negativeWords.forEach(word => {
    if (textLower.includes(word)) negCount++;
  });
  
  let rating, confidence;
  
  if (posCount > negCount) {
    rating = Math.min(5, 3 + posCount - negCount);
    confidence = Math.min(0.9, 0.5 + (posCount - negCount) * 0.1);
  } else if (negCount > posCount) {
    rating = Math.max(1, 3 - (negCount - posCount));
    confidence = Math.min(0.9, 0.5 + (negCount - posCount) * 0.1);
  } else {
    rating = 3;
    confidence = 0.5;
  }
  
  return {
    rating: rating,
    confidence: confidence,
    note: "Résultat généré par le mode simulation"
  };
}

/**
 * Generate a simulated summary of the text.
 * 
 * @param {string} text - The text to summarize
 * @param {boolean} error - Whether an error occurred
 * @returns {string} A simulated summary
 */
function simulateSummary(text, error = false) {
  if (error) {
    return "Impossible de générer un résumé. (Mode simulation - erreur OpenAI)";
  }
  
  // Simple summarization - take first and last sentence
  const sentences = text.split('.');
  if (sentences.length <= 2) {
    return text;
  }
  
  const summary = `${sentences[0].trim()}... ${sentences[sentences.length - 2].trim()}.`;
  return `${summary}\n\n(Résumé généré par le mode simulation)`;
}

module.exports = {
  chatCompletion,
  analyzeSentiment,
  summarizeText
};
