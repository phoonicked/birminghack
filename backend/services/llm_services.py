# services/llm_service.py
import os
from openai import OpenAI
from dotenv import load_dotenv
import config

load_dotenv()

# Create an OpenAI client instance using your API key
openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

def generate_llm_text(prompt, instructions=None, model="gpt-4o"):
    """
    Generate text using the new OpenAI API client.
    
    Parameters:
      - prompt (str): The user prompt.
      - instructions (str, optional): Developer instructions (e.g., "Talk like a pirate.").
      - model (str): The model to use (default is "gpt-4o").
      
    Returns:
      The generated text (str).
    """
    messages = []
    if instructions:
        messages.append({"role": "developer", "content": instructions})
    messages.append({"role": "user", "content": prompt})
    
    # Use the chat completions endpoint
    completion = openai_client.chat.completions.create(
        model=model,
        messages=messages,
    )
    
    return completion.choices[0].message.content.strip()
