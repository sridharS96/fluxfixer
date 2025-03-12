import google.generativeai as genai
import json
import os
import logging
import subprocess
import argparse
import re
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Generative AI client
try:
    genai.configure(api_key="AIzaSyB4TJyi_FROT9nOhdqsPtK3060AxChlKVc")  # Replace with your API key
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    logger.error(f"Error initializing Generative AI client: {e}")
    exit()

# Function to parse lint results for SQL
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

# Function to generate fixed query SQL
def generate_fixed_query(lint_results, original_query):
    contents = f"""
    Given the following SQL query and linting errors, 
    Original Query:
    {original_query}

    Lint Errors:
    {lint_results}

    Fix the query according to the lint results and provide the fixed SQL query.
    
     Consider the following: 
     1. sql must not begin with newlines or whitespace. No trailing whitespace is allowed. No tabs are allowed. Remove first empty line.
     2. Avoid using SQL keywords like 'date,' 'quarter,' or 'year' as column names. Rename them to more appropriate alternatives.. 
     3. SQL query must not begin with newlines or whitespace. No trailing whitespace is allowed. No tabs are allowed. Remove first empty line.
     4. Add exactly one empty newline character between the closing parenthesis of a CTE and the start of the next CTE. Still add the comma of the next cte at the end of the line of previous cte and then newline.
     5. Add semicolon at the end of the separate sql query in end of line. 
     6. Add comma for next columns at the end of line. 
     7. Replace any '*' with used columns in the below queries unless there is no generate date array.
     8. Qualify all columns with table names.
     9. give alias to all tables and use alias in the query.
     10. Rename any SQL keywords like "date", "quarter", "year" to something appropirate.
     11. Follow proper formatting and naming conventions throughout.
    """
    try:
        response = model.generate_content(contents)
        match = re.search(r'```sql\n(.*?)```', response.text, re.DOTALL)
        fixed_query = match.group(1).strip() + "\n" 
    except Exception as e:
        logger.error(f"Error generating fixed query: {e}")
        return None  # return none if there is an error

    return fixed_query

# Main function to process the scripts and generate fixed queries
def main(script_name, input_path, error_path, fixed_path,fluff_config):
    print(f"[*]Fix Started for {input_path}")
    input_file = input_path
    error_file = os.path.join(error_path, script_name + '.err')
    fixed_file = os.path.join(fixed_path, script_name)

    # Read the original query from the input file
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            original_query = file.read()
            print(f"[*]File Available in {input_path}")
    except FileNotFoundError:
        logger.error(f"Error: {script_name} ::::: {input_file} file not found.")
        return
    print(f"[*]Lint Fix Started for {input_path}")
    # Run sqlfluff lint command
    lint_command = ["sqlfluff", "lint", input_file, "--dialect=bigquery", "--format=json", f"--config={fluff_config}"]
    #print(f"Linting command: {' '.join(lint_command)}")
    lint_results = subprocess.run(lint_command, capture_output=True, text=True)
    print(f"Linting for file: {input_file}")
    
    

    # Ensure the directory exists before writing the error file
    os.makedirs(os.path.dirname(error_file), exist_ok=True)

    readable_output = parse_lint_results(json.loads(lint_results.stdout))
    print(f"[*]Lint Errors Result Write Started for {input_path}")
    #print(readable_output)
    # Write the lint errors to the error file
    try:
        with open(error_file, "w", encoding="utf-8") as file:
            file.write(readable_output)
        logger.info(f"Errors written to {error_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing errors to {error_file}: {e}")
    
    print(f"[*]Lint Errors Result Write Completed for {input_path}")

    print(f"[*]Processing Fix for {input_path}")

    # Get the fixed query
    fixed_query = generate_fixed_query(readable_output, original_query)

    if fixed_query is None:
        return  # stop the function if the query generation failed.

    # Ensure the directory exists before writing the fixed query file
    os.makedirs(os.path.dirname(fixed_file), exist_ok=True)
    
    print(f"[*]Fix Completed for {input_path}")

    # Write the fixed query to the file
    try:
        with open(fixed_file, "w", encoding="utf-8") as file:
            file.write(fixed_query)
        logger.info(f"Fixed query written to {fixed_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing fixed query to {fixed_file}: {e}")
    
    

def final_run_sqlfluff(script_name,fixed_file, fluff_config, dialect="bigquery"): #correct function definition
    print(f"Linting for file: {fixed_file}")
    # Read the original query from the input file
    try:
        with open(fixed_file, "r", encoding="utf-8") as file:
            original_query = file.read()
    except FileNotFoundError:
        logger.error(f"Error: {script_name} ::::: {fixed_file} file not found.")
        return
    try:
        if not os.path.exists(fixed_file): #correct condition
            logger.error(f"File not found: {fixed_file}")
            return
        logger.info(f"Linting fixed file: {fixed_file}")
        try:
            result = subprocess.run(
                ["sqlfluff", "lint", fixed_file, f"--dialect={dialect}", f"--config={fluff_config}"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(result.stdout)  # Print the lint results.
            #print(result.stdout) 
        except subprocess.CalledProcessError as e:
            logger.error(f"Linting failed for {fixed_file}: {e}")
            logger.error(e.stderr)  # print stderr.
        except FileNotFoundError:
            logger.error("sqlfluff not found. Ensure it's installed and in your PATH.")
            return
        except Exception as e:
            logger.error(f"An unexpected error occurred while linting {fixed_file}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

# Argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process SQL files with linting and fix queries.")
    parser.add_argument("changed_files", nargs='+', help="Path to the input SQL file(s).")
    parser.add_argument("error_path", help="Path to the output error file.")
    parser.add_argument("fixed_path", help="Path to the output fixed SQL file.")
    parser.add_argument("fluff_config", help="SQLfluff config file.")
    args = parser.parse_args()

    # Process each file in the input_path list
    print(f"Processing {len(args.changed_files)} files...")
    for input_file in args.changed_files:
        script_name = os.path.basename(input_file)  # Get the filename.
        main(script_name, input_file, args.error_path, args.fixed_path, args.fluff_config) #pass the script name, input file, error path, fixed path, fluff config
        fixed_file = os.path.join(args.fixed_path, script_name) #create the fixed file path.
        final_run_sqlfluff(script_name,fixed_file, args.fluff_config) #pass the fixed file path. fluff config
