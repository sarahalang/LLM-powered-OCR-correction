# Date: 2024-10-15
# Creator: SL with assistance by GPT ( https://chatgpt.com/c/670e27b8-88b0-8012-90f4-92290dbc4c52 )
# State: works

import os

def list_subdirectories(parent_path):
    """
    Lists all subdirectories within the given parent directory.

    Parameters:
    - parent_path (str): Path to the parent directory.

    Returns:
    - List of subdirectory names.
    """
    try:
        subdirs = [
            name for name in os.listdir(parent_path)
            if os.path.isdir(os.path.join(parent_path, name))
        ]
        return subdirs
    except FileNotFoundError:
        print(f"Error: The directory '{parent_path}' does not exist.")
        return []
    except Exception as e:
        print(f"Unexpected error while listing subdirectories: {e}")
        return []

def generate_git_diff_commands_for_subdir(subdir_path, subdir_name):
    """
    Generates git diff commands for each pair of input and output text files
    in the specified sub-directory.

    Parameters:
    - subdir_path (str): Path to the specific [PDF_name] directory.
    - subdir_name (str): Name of the sub-directory (used for comments).

    Returns:
    - List of git diff commands as strings.
    """
    git_diff_commands = []

    # Define paths for transkribus-output and gpt-output
    transkribus_output_path = os.path.join(subdir_path, 'transkribus-output')
    gpt_output_path = os.path.join(subdir_path, 'gpt-output')

    # Check if both directories exist
    if not os.path.isdir(transkribus_output_path):
        print(f"Warning: '{transkribus_output_path}' does not exist. Skipping '{subdir_name}'.")
        return git_diff_commands
    if not os.path.isdir(gpt_output_path):
        print(f"Warning: '{gpt_output_path}' does not exist. Skipping '{subdir_name}'.")
        return git_diff_commands

    # List all .txt files in transkribus-output
    transkribus_txt_files = [
        f for f in os.listdir(transkribus_output_path)
        if os.path.isfile(os.path.join(transkribus_output_path, f)) and f.lower().endswith('.txt')
    ]

    if not transkribus_txt_files:
        print(f"Info: No .txt files found in '{transkribus_output_path}'.")
        return git_diff_commands

    # Iterate over each .txt file and generate git diff commands
    for txt_file in transkribus_txt_files:
        input_txt_path = os.path.join(transkribus_output_path, txt_file)
        output_txt_path = os.path.join(gpt_output_path, txt_file)

        # Check if the corresponding output file exists
        if not os.path.isfile(output_txt_path):
            print(f"Warning: Output file '{output_txt_path}' does not exist. Skipping '{txt_file}'.")
            continue

        # Generate relative paths for the git commands
        # Assuming the script is run from the root directory containing 'data/'
        rel_input_path = os.path.relpath(input_txt_path)
        rel_output_path = os.path.relpath(output_txt_path)

        # Create the two git diff commands, ending with a semicolon
        cmd1 = f"git diff --color-words=. {rel_input_path} {rel_output_path};"
        cmd2 = f'git diff --word-diff=color --word-diff-regex="[ ]+|[^ ]+" {rel_input_path} {rel_output_path};'

        # Optionally, add comments or section headers for clarity
        git_diff_commands.append(f"# Comparing '{txt_file}' in '{subdir_name}'")
        git_diff_commands.append(cmd1)
        git_diff_commands.append(cmd2)
        git_diff_commands.append("")  # Add an empty line for readability

    return git_diff_commands

def prompt_user_to_select_subdir(subdirs):
    """
    Prompts the user to select a sub-directory from the provided list.

    Parameters:
    - subdirs (list): List of subdirectory names.

    Returns:
    - Selected subdirectory name (str) or None if selection is invalid.
    """
    if not subdirs:
        print("No subdirectories available to process.")
        return None

    print("Available sub-directories to process:")
    for idx, subdir in enumerate(subdirs, start=1):
        print(f"{idx}. {subdir}")

    while True:
        try:
            choice = input(f"Enter the number of the sub-directory you want to process (1-{len(subdirs)}): ").strip()
            if not choice:
                print("No input provided. Exiting.")
                return None
            choice_num = int(choice)
            if 1 <= choice_num <= len(subdirs):
                return subdirs[choice_num - 1]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(subdirs)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    # Define the path to the 'ocr-correction' directory
    OCR_CORRECTION_PATH = os.path.join('data', 'ocr-correction')

    # List all subdirectories within 'ocr-correction'
    subdirs = list_subdirectories(OCR_CORRECTION_PATH)

    if not subdirs:
        return

    # Prompt the user to select a sub-directory
    selected_subdir = prompt_user_to_select_subdir(subdirs)

    if not selected_subdir:
        return

    # Define the path to the selected sub-directory
    selected_subdir_path = os.path.join(OCR_CORRECTION_PATH, selected_subdir)

    # Generate git diff commands for the selected sub-directory
    git_diff_commands = generate_git_diff_commands_for_subdir(selected_subdir_path, selected_subdir)

    if not git_diff_commands:
        print(f"No git diff commands generated for '{selected_subdir}'.")
        return

    # Define the output .txt file name based on the selected sub-directory
    sanitized_subdir_name = selected_subdir.replace(" ", "_")  # Replace spaces with underscores for filenames
    OUTPUT_FILE = f'git_diff_commands_{sanitized_subdir_name}.txt'

    # Write the commands to the output file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(git_diff_commands))
        print(f"Git diff commands have been successfully written to '{OUTPUT_FILE}'.")
    except Exception as e:
        print(f"Error writing to '{OUTPUT_FILE}': {e}")

if __name__ == "__main__":
    main()
