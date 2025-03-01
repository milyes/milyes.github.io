/**
 * Utility functions for interacting with OpenAI API.
 */

const OpenAI = require('openai');

// the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
// do not change this unless explicitly requested by the user
const DEFAULT_MODEL = "gpt-4o";

// Initialize OpenAI client
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

/**
 * Generate a response using OpenAI's chat completion.
 * 
 * @param {string} prompt - The user's message or question
 * @param {string} [model=DEFAULT_MODEL] - The model to use
 * @returns {Promise<string>} The generated response
 */
async function chatCompletion(prompt, model = DEFAULT_MODEL) {
  try {
    const response = await openai.chat.completions.create({
      model: model,
      messages: [{ role: "user", content: prompt }],
    });
    
    return response.choices[0].message.content;
  } catch (error) {
    console.error(`Error in chat completion: ${error.message}`);
    throw new Error(`Failed to get chat completion: ${error.message}`);
  }
}

/**
 * Analyze the sentiment of a given text.
 * 
 * @param {string} text - The text to analyze
 * @returns {Promise<Object>} A dictionary with sentiment rating and confidence
 */
async function analyzeSentiment(text) {
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
    throw new Error(`Failed to analyze sentiment: ${error.message}`);
  }
}

/**
 * Generate a concise summary of the input text.
 * 
 * @param {string} text - The text to summarize
 * @returns {Promise<string>} The generated summary
 */
async function summarizeText(text) {
  try {
    const prompt = `Please summarize the following text concisely while maintaining key points:\n\n${text}`;
    const response = await openai.chat.completions.create({
      model: DEFAULT_MODEL,
      messages: [{ role: "user", content: prompt }],
    });
    
    return response.choices[0].message.content;
  } catch (error) {
    console.error(`Error in text summarization: ${error.message}`);
    throw new Error(`Failed to summarize text: ${error.message}`);
  }
}

module.exports = {
  chatCompletion,
  analyzeSentiment,
  summarizeText
};
