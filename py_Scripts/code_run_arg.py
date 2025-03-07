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


# Function to parse lint results fo SQL
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
                            readable_output += f"  - Line {line_no}, Column {line_pos}: {description}\n"
                        else:
                            readable_output += "  - Invalid violation format.\n"
            else:
                readable_output += " - No violations found in this section.\n"
        else:
            readable_output += " - Invalid result format.\n"

    return readable_output
###################################################################################################################

# Function to generate fixed query SQL
def generate_fixed_query(lint_results, original_query):
    contents = f"""
    Given the following SQL query and linting errors, 
    Original Query:
    {original_query}

    Lint Errors:
    {lint_results}

    Fix the query according to the lint results and provide the fixed SQL query for bigquery without any comments or markdown code blocks , add semicolon at the end of the seprate sql query , comma at the end of line
    consider the following: 1. Remove any comments 3. Add semicolon at the end of the separate sql query 4. Add comma at the end of line
    5. Remove any markdown code blocks 6. Add semicolon at the end of the separate sql query in the newline 7. Add comma at the end of line 8. Files must not begin with newlines or whitespace.
    8. Remove any '*' with used columns in the below queries.
    9. Remove any extra spaces in the query.  10.Blank line expected but not found after CTE closing bracket.
    """
    try:
        response = model.generate_content(contents)
        fixed_query = response.text
    except Exception as e:
        logger.error(f"Error generating fixed query: {e}")
        return None #return none if there is an error

    return fixed_query
###################################################################################################################


# Main function to process the scripts and generate fixed queries
def main(script_name, input_path, error_path, fixed_path):

    input_file = input_path
    error_file = os.path.join(error_path, script_name + '.err')
    fixed_file = os.path.join(fixed_path, script_name)

    # Read the original query from the input file
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            original_query = file.read()
    except FileNotFoundError:
        logger.error(f"Error: {script_name} ::::: {input_file} file not found.")
        return

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
        logger.info(f"Errors written to {error_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing errors to {error_file}: {e}")

    # Get the fixed query
    fixed_query = generate_fixed_query(readable_output, original_query)

    if fixed_query is None:
        return #stop the function if the query generation failed.

    # Ensure the directory exists before writing the fixed query file
    os.makedirs(os.path.dirname(fixed_file), exist_ok=True)

    # Write the fixed query to the file
    try:
        with open(fixed_file, "w", encoding="utf-8") as file:
            file.write(fixed_query.replace("```sql", "").replace("```", ""))
        logger.info(f"Fixed query written to {fixed_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing fixed query to {fixed_file}: {e}")

# Argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process SQL files with linting and fix queries.")
   # parser.add_argument("script_name", help="Name of the script being processed.")
    parser.add_argument("changed_files", nargs='+', help="Path to the input SQL file(s).")
    parser.add_argument("error_path", help="Path to the output error file.")
    parser.add_argument("fixed_path", help="Path to the output fixed SQL file.")
    args = parser.parse_args()

    # Process each file in the input_path list
    for input_file in args.changed_files:
        script_name = os.path.basename(input_file) #Get the filename.
        main(script_name, input_file, args.error_path, args.fixed_path)