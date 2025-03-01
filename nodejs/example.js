#!/usr/bin/env node
/**
 * Example script demonstrating direct use of OpenAI utilities.
 */

const { chatCompletion, analyzeSentiment, summarizeText } = require('./openai_utils');

/**
 * Example function demonstrating the OpenAI utilities.
 * Set OPENAI_API_KEY environment variable before running this script.
 */
async function main() {
  // Check if API key is set
  if (!process.env.OPENAI_API_KEY) {
    console.error("Error: OPENAI_API_KEY environment variable is not set.");
    console.error("Set it with: export OPENAI_API_KEY='your-api-key-here'");
    return;
  }
  
  console.log("OpenAI API Example Script");
  console.log("-------------------------");
  
  try {
    // Chat completion example
    console.log("\n1. Chat Completion Example:");
    const question = "What are three benefits of using Node.js for web development?";
    console.log(`Question: ${question}`);
    
    const answer = await chatCompletion(question);
    console.log(`Answer: ${answer}`);
    
    // Sentiment analysis example
    console.log("\n2. Sentiment Analysis Example:");
    const sampleText = "I'm extremely happy with the results of this project. It's been a wonderful experience!";
    console.log(`Text: ${sampleText}`);
    
    const sentiment = await analyzeSentiment(sampleText);
    console.log(`Sentiment Rating: ${sentiment.rating}/5`);
    console.log(`Confidence: ${sentiment.confidence.toFixed(2)}`);
    
    // Text summarization example
    console.log("\n3. Text Summarization Example:");
    const longText = `
      Node.js is an open-source, cross-platform JavaScript runtime environment that executes JavaScript code outside 
      of a web browser. Node.js lets developers use JavaScript to write command line tools and for server-side 
      scripting—running scripts server-side to produce dynamic web page content before the page is sent to the 
      user's web browser. Consequently, Node.js represents a "JavaScript everywhere" paradigm, unifying web 
      application development around a single programming language, rather than different languages for server-
      side and client-side scripts. Though .js is the standard filename extension for JavaScript code, the name 
      "Node.js" doesn't refer to a particular file in this context and is merely the name of the product.
    `;
    console.log(`Original Text: ${longText.substring(0, 100)}...`);
    
    const summary = await summarizeText(longText);
    console.log(`Summary: ${summary}`);
    
    console.log("\nAll examples completed successfully!");
  } catch (error) {
    console.error(`An error occurred: ${error.message}`);
  }
}

main();
