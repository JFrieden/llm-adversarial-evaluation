import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
API_KEY = os.getenv('CLAUDE_API_KEY')

# Base API endpoint
BASE_URL = "https://api.anthropic.com/v1/messages"

def send_message_to_claude(prompt, model="claude-3-haiku-20240307"):
    """
    Send a message to Claude and receive a response.
    
    :param prompt: The user's message to Claude
    :param model: The Claude model to use (default is Haiku)
    :return: Claude's response text
    """
    # Prepare the request headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "Anthropic-Version": "2023-06-01"
    }
    
    # Prepare the request payload
    payload = {
        "model": model,
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        # Send the request to the Claude API
        response = requests.post(BASE_URL, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Extract and return Claude's response
        return response.json()['content'][0]['text']
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def main():
    # Example usage
    prompt = "Hello Claude, how are you today?"
    response = send_message_to_claude(prompt)
    
    if response:
        print("Claude's response:")
        print(response)

if __name__ == "__main__":
    main()