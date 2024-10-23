# Date: 2024-10-15
# Creator: SL with assistance by GPT ( https://chatgpt.com/c/670e06c4-210c-8012-8726-13f00440cc94 )
# State: Updated for OpenAI API >=1.0.0; finally got this to work by pip install openai==0.28

import os
import openai

# Paths for the project keys and data
KEYS_PATH = 'project-keys'
DATA_PATH = 'data/ocr-correction'

# Load API key and project ID
with open(os.path.join(KEYS_PATH, 'ocr-key.txt'), 'r') as file:
    api_key = file.read().strip()

with open(os.path.join(KEYS_PATH, 'OCR-Correction.txt'), 'r') as file:
    project_id = file.read().strip()

# Set the OpenAI API key
openai.api_key = api_key

# Define the custom prompt as a system message
custom_prompt = (
    "You're an expert academic OCR corrector for historical text. You do this by comparing a supplied initial OCR/HTR output "
    "with the original image from which it was transcribed. The goal is to produce a perfect diplomatic transcription, following the transcription "
    "rules of the original document as evident from the provided base transcription. These rules include silently expanding certain abbreviations, normalizing "
    "i/j and u/v, and using the logical negation sign (¬) to indicate a line break within a word. Additionally, it removes OCR artifacts or junk characters "
    "from faulty OCR transcription. The output must retain the original text structure (e.g., line breaks) to support version control visualization. "
    "The text may contain multiple languages, predominantly Latin, and special characters (e.g., ℞, ℈, ℔, and alchemical symbols) should be accurately "
    "represented using their Unicode values. If unsure about a special character, represent it as '@'. Output only the corrected text."
)

# Function to process each text with GPT using the custom prompt
def process_with_gpt(text_content, custom_prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use a valid model like 'gpt-3.5-turbo' or 'gpt-4'
            # For example, these are available:
            # gpt-4o-mini - war für diesen Task nicht unbedingt besser und 3x so teuer
            # gpt-3.5-turbo
            messages=[
                {"role": "system", "content": custom_prompt},
                {"role": "user", "content": text_content}
            ],
            max_tokens=1500,  # Adjust as needed based on response length
            temperature=0.7
        )
        # Extract the assistant's reply
        corrected_text = response.choices[0].message['content'].strip()
        return corrected_text
    except openai.error.OpenAIError as e:
        # Handle OpenAI API errors
        return f"OpenAI API error: {e}"
    except Exception as e:
        # Handle other possible errors
        return f"Unexpected error: {e}"

# Get user input for specific sub-directory (PDF file) to process
subdir = input("Enter the name of the OCR sub-directory (PDF file) you want to process: ")

# Define paths based on the chosen sub-directory
subdir_path = os.path.join(DATA_PATH, subdir)
transkribus_output_path = os.path.join(subdir_path, 'transkribus-output')
gpt_output_path = os.path.join(subdir_path, 'gpt-output')

# Check if the sub-directory exists
if not os.path.exists(subdir_path):
    print(f"The sub-directory '{subdir}' does not exist. Please check the name and try again.")
else:
    # Ensure gpt-output directory exists
    os.makedirs(gpt_output_path, exist_ok=True)

    # Process each OCR page in the transkribus-output directory
    for txt_file in os.listdir(transkribus_output_path):
        # Define file paths
        txt_path = os.path.join(transkribus_output_path, txt_file)
        image_path = os.path.join(subdir_path, 'images', os.path.splitext(txt_file)[0] + '.jpg')  # Adjusted for .jpg
        output_path = os.path.join(gpt_output_path, txt_file)

        # Read the OCR text content
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
        except FileNotFoundError:
            print(f"File not found: {txt_path}")
            continue
        except Exception as e:
            print(f"Error reading {txt_file}: {e}")
            continue

        # Process the text with GPT
        corrected_text = process_with_gpt(text_content, custom_prompt)

        # Check if the response contains an error message
        if corrected_text.startswith("OpenAI API error") or corrected_text.startswith("Unexpected error"):
            print(f"Failed to process {txt_file}: {corrected_text}")
            continue

        # Save the corrected text to the gpt-output directory
        try:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(corrected_text)
            print(f"Processed and saved: {output_path}")
        except Exception as e:
            print(f"Failed to save {txt_file}: {e}")
