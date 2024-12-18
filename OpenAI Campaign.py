import openai
import json
import time
import pandas as pd
from Jailbreaks import *
from dotenv import load_dotenv
import os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import tqdm
import base64
import logging

# Load environment variables
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

# Define your attack functions
attack_functions = {
    # "base64_in_out": base64_in_out,
    # "base64_in": base64_in,
    # "base64_out": base64_out,
    # "prefix_injection": prefix_injection,
    # "style_injection_short": style_injection_short,
    # "evil_prefix_injection": evil_prefix_injection,
    # "refusal_suppresion": refusal_suppresion,
    # "style_injection_json": style_injection_json,
    # "distractors": distractors,
    # "website": website,
    # "wikipedia": wikipedia,
    # "combination_3": combination_3,
    # "refusal_suppresion_short_injection": refusal_suppresion_short_injection,
    # "combination_4": combination_4,
    # "base64_in_out_strict": base64_in_out_strict,
    "spanish_leet": spanish_leet_speak,
    "instruct_spanish_leet": instruct_spanish_leet
}

# Load the prompts from the JSON file
with open("openai_redteam_prompts.json", "r", encoding='utf-8') as file:
    red_team_prompts = json.load(file)

# Function to generate OpenAI responses based on the attack and prompt
def get_openai_response(client: OpenAI, prompt: str, model="gpt-4"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during OpenAI request: {e}")
        return ""

# Function to process a single prompt-attack pair
def process_attack(client, attack_type, prompt, attack_name, attack_function, model="gpt-4-turbo"):
    attack_prompt = attack_function(prompt)
    response = get_openai_response(client, attack_prompt, model)

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
    client = OpenAI()
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
                    futures.append(executor.submit(process_attack, client, attack_type, prompt, attack_name, attack_function))
        
        # Collect the results as they complete
        for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
            results.append(future.result())

    # Convert results to a DataFrame
    df = pd.DataFrame(results)
    return df

# Run the evaluation and save the results
target_model = "gpt-4o-mini"
df_results = evaluate_attacks()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save results to a CSV for analysis
output_file = f"openai_campaign/{target_model}_attack_responses_{timestamp}.csv"
df_results.to_csv(output_file, index=False)
print(f"Results saved to {output_file}")

# Optionally: Display the first few rows
print(df_results.head())
