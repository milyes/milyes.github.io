#!/usr/bin/env python3
"""
Example script demonstrating direct use of OpenAI utilities.
"""

import os
from openai_utils import chat_completion, analyze_sentiment, summarize_text

def main():
    """
    Example function demonstrating the OpenAI utilities.
    Set OPENAI_API_KEY environment variable before running this script.
    """
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("OpenAI API Example Script")
    print("-------------------------")
    
    # Chat completion example
    print("\n1. Chat Completion Example:")
    question = "What are three benefits of using Python for web development?"
    print(f"Question: {question}")
    
    answer = chat_completion(question)
    print(f"Answer: {answer}")
    
    # Sentiment analysis example
    print("\n2. Sentiment Analysis Example:")
    sample_text = "I'm extremely happy with the results of this project. It's been a wonderful experience!"
    print(f"Text: {sample_text}")
    
    sentiment = analyze_sentiment(sample_text)
    print(f"Sentiment Rating: {sentiment['rating']}/5")
    print(f"Confidence: {sentiment['confidence']:.2f}")
    
    # Text summarization example
    print("\n3. Text Summarization Example:")
    long_text = """
    Python is a high-level, interpreted programming language created by Guido van Rossum and released in 1991. 
    It emphasizes code readability with its notable use of significant whitespace. Its language constructs and 
    object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.
    Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including procedural, 
    object-oriented, and functional programming. Python is often described as a "batteries included" language due to 
    its comprehensive standard library.
    """
    print(f"Original Text: {long_text[:100]}...")
    
    summary = summarize_text(long_text)
    print(f"Summary: {summary}")
    
    print("\nAll examples completed successfully!")

if __name__ == "__main__":
    main()
