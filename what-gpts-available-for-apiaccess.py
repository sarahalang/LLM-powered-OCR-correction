# Date: 2024-10-15
# Creator: SL with assistance by GPT ( https://chatgpt.com/c/670e06c4-210c-8012-8726-13f00440cc94 )
# State: works

import openai
import os
import requests

# Load API key
KEYS_PATH = 'project-keys'
with open(os.path.join(KEYS_PATH, 'ocr-key.txt'), 'r') as file:
    api_key = file.read().strip()

# OpenAI API endpoint for listing models
url = "https://api.openai.com/v1/models"

# Define the headers including your API key
headers = {
    "Authorization": f"Bearer {api_key}"
}

# Make the request to the OpenAI API to list models
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    models = response.json()['data']
    print("Available models:")
    for model in models:
        print(model['id'])
else:
    print(f"Failed to retrieve models. Status code: {response.status_code}")
    print(response.json())
