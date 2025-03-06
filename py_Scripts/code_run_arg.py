import google.generativeai as genai
import json
import os
import logging
import subprocess
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Generative AI client
try:
    genai.configure(api_key="AIzaSyACEevcT6nND-gwFTdqoP_d54USObCbOdk")
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    logger.error(f"Error initializing Generative AI client: {e}")
    exit()

# Function to parse lint results
def parse_lint_results(lint_results):
    readable_output = "Linting Results:\n"
    if not lint_results:
        readable_output += "No linting results found.\n"
        return readable_output

    for result in lint_results:
        if isinstance(result, dict):
            if 'violations' in result and isinstance(result['violations'], list):
                if not result['violations']:
                    readable_output += " - No violations found in this section.\n"
                else:
                    for violation in result['violations']:
                        if isinstance(violation, dict):
                            line_no = violation.get('start_line_no', 'N/A')
                            line_pos = violation.get('start_line_pos', 'N/A')
                            description = violation.get('description', 'N/A')
                            readable_output += f"   - Line {line_no}, Column {line_pos}: {description}\n"
                        else:
                            readable_output += "   - Invalid violation format.\n"
            else:
                readable_output += " - No violations found in this section.\n"
        else:
            readable_output += " - Invalid result format.\n"

    return readable_output

# Function to generate fixed query
def generate_fixed_query(lint_results, original_query):
    contents = f"""
    Given the following SQL query and linting errors, modify the query to fix the issues:

    Original Query:
    {original_query}

    Lint Errors:
    {lint_results}

    Fix the query according to the lint results and provide the fixed SQL query for bigquery without any comments or markdown code blocks , add semicolon at the end of the seprate sql query:
    """
    try:
        response = model.generate_content(contents)
        fixed_query = response.text
    except Exception as e:
        logger.error(f"Error generating fixed query: {e}")
        exit()
    return fixed_query

# Main function to process the script
def main(script_name, input_path, error_path, fixed_path):
   
    input_file = input_path 
    error_file = error_path + "\\"+ script_name+'.err'
    fixed_file = fixed_path + "\\"+ script_name
    # Read the original query from the input file
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            original_query = file.read()
    except FileNotFoundError:
        logger.error(f"Error: {script_name} ::::: {input_file} file not found.")
        exit()

    # Run sqlfluff lint command
    lint_command = ["sqlfluff", "lint", input_file, "--dialect=bigquery", "--format=json"]
    lint_results = subprocess.run(lint_command, capture_output=True, text=True)
    
    # Ensure the directory exists before writing the error file
    os.makedirs(os.path.dirname(error_file), exist_ok=True)
    
    readable_output = parse_lint_results(json.loads(lint_results.stdout))
    # Write the lint errors to the error file
    try:
        with open(error_file, "w") as file:
            file.write(readable_output)
        logger.info("Errors written to file successfully.")
    except Exception as e:
        logger.error(f"Error writing errors to file: {e}")

    # Get the fixed query
    fixed_query = generate_fixed_query(readable_output, original_query)

    # Ensure the directory exists before writing the fixed query file
    os.makedirs(os.path.dirname(fixed_file), exist_ok=True)

    # Write the fixed query to the file
    try:
        with open(fixed_file, "w") as file:
            file.write(fixed_query.replace("```sql", "").replace("```", "")  )
        logger.info("Fixed query written to file successfully.")
    except Exception as e:
        logger.error(f"Error writing fixed query to file: {e}")

# Argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process SQL files with linting and fix queries.")
    parser.add_argument("script_name", help="Name of the script being processed.")
    parser.add_argument("input_path", help="Path to the input SQL file.")
    parser.add_argument("error_path", help="Path to the output error file.")
    parser.add_argument("fixed_path", help="Path to the output fixed SQL file.")
    args = parser.parse_args()

    main(args.script_name, args.input_path, args.error_path, args.fixed_path)
