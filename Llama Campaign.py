import requests
import json
import time
import pandas as pd
from Jailbreaks import *
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import tqdm
import base64
import requests

# Load environment variables
load_dotenv()
API_KEY = os.getenv('HF_KEY')

# Base API endpoint
BASE_URL = "https://wne46ayrz9gdo7te.us-east-1.aws.endpoints.huggingface.cloud"

# Define your attack functions
attack_functions = {
    "base64_in_out": base64_in_out,
    "base64_in": base64_in,
    "base64_out": base64_out,
    "prefix_injection": prefix_injection,
    "style_injection_short": style_injection_short,
    "evil_prefix_injection": evil_prefix_injection,
    "refusal_suppresion": refusal_suppresion,
    "style_injection_json": style_injection_json,
    "distractors": distractors,
    "website": website,
    "wikipedia": wikipedia,
    "combination_3": combination_3,
    "refusal_suppresion_short_injection": refusal_suppresion_short_injection,
    "combination_4": combination_4,
    "base64_in_out_strict": base64_in_out_strict,
    "spanish_leet": spanish_leet_speak,
    "instruct_spanish_leet": instruct_spanish_leet
}

# Load the prompts from the JSON file
with open("openai_redteam_prompts.json", "r", encoding='utf-8') as file:
    red_team_prompts = json.load(file)

import logging
import time

def get_llama_response(prompt, model="llama-3-70b-instruct", max_retries=3):
    """
    Send a message to Llama-3-70b-instruct with retry logic and more robust error handling.
    
    :param prompt: The user's message to Claude
    :param model: The Claude model to use (default is Haiku)
    :param max_retries: Number of times to retry the request
    :return: Claude's response text
    """
    headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Accept" : "application/json",
                "Content-Type": "application/json"
            }

    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
        }
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(BASE_URL, headers=headers, json=payload)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = (2 ** attempt)  # Exponential backoff
                logging.warning(f"Rate limited. Waiting {wait_time} seconds before retry.")
                time.sleep(wait_time)
                continue
                        
            return response.json()[0]['generated_text']
        
        except requests.RequestException as e:
            logging.error(f"Request error on attempt {attempt + 1}: {e}")
            logging.error(f"Response content: {response.content}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(e)
            return None

    return None


def process_attack(attack_type, prompt, attack_name, attack_function, model="llama-3-70b-instruct"):
    attack_prompt = attack_function(prompt)
    response = get_llama_response(attack_prompt, model)
    
    # Improved base64 decoding
    try:
        if ('base64' in attack_name or 'combination' in attack_name) and response:
            # Add padding if necessary
            response_decoded = base64.b64decode(response + '=' * (-len(response) % 4)).decode('utf-8')
        else:
            response_decoded = response or ""
    except Exception as e:
        print(f"Base64 decoding error for {attack_name}: {e}")
        logging.warning(f"Base64 decoding error for {attack_name}: {e}\nWhile decoding response: {response}")
        response_decoded = response or ""
    
    return {
        'attack_type': attack_type,
        'prompt': prompt,
        'attack_name': attack_name,
        'attack_prompt': attack_prompt,
        'response': response,
        'response_decoded': response_decoded
    } 

# Function to apply attacks and evaluate model responses
def evaluate_attacks():
    results = []
    futures = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
        # Loop over each category in the red team prompts
        for i, category in enumerate(red_team_prompts['report_red_team_prompts']):
            attack_type = category['type']
            prompts = category['prompts']
            print(f"Processing {attack_type} prompts...")
            
            # Apply each attack function to each prompt
            for j, prompt in tqdm.tqdm(enumerate(prompts)):
                for attack_name, attack_function in attack_functions.items():
                    futures.append(executor.submit(process_attack, attack_type, prompt, attack_name, attack_function))
        
        # Collect the results as they complete
        for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
            results.append(future.result())

    # Convert results to a DataFrame
    df = pd.DataFrame(results)
    return df

# Run the evaluation and save the results
target_model = "llama-3-70b-instruct"
df_results = evaluate_attacks()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save results to a CSV for analysis
output_file = f"llama_campaign/{target_model}_attack_responses_{timestamp}.csv"
df_results.to_csv(output_file, index=False)
print(f"Results saved to {output_file}")

# Optionally: Display the first few rows
print(df_results.head())

