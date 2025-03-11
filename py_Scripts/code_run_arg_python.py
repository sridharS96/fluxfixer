import google.generativeai as genai
import json
import os
import logging
import subprocess
import argparse
import tempfile
import re
import jsonlint 
from jsonschema import Draft7Validator, SchemaError, ValidationError

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
    
# Function to generate fixed Python Code
def generate_fixed_python_code(lint_results, original_code):
    contents = f"""
      Given the following Python code and its linting errors, modify the code to fix the issues:
       Original Code:
       {original_code}
       
       Linting Errors:
       {lint_results}
       
       Your task is to:
       1. Fix all linting issues while ensuring the code adheres to PEP 8 standards.
       2. Correct syntax errors and structural issues to ensure the code runs without errors.
       3. Maintain the original logic and functionality of the code.
       4. Ensure proper indentation, spacing, and formatting.
       5. Ensure only declared variables are used, and follow proper naming conventions.
       6. Provide only the corrected code output with no explanations or additional text.
         """
    try:
        response = model.generate_content(contents)
        match = re.search(r'```python\n(.*?)```', response.text, re.DOTALL)
        fixed_code = match.group(1).strip() 
    except Exception as e:
        logger.error(f"Error generating fixed code: {e}")
        return None #return none if there is an error

    return fixed_code
###################################################################################################################

def parse_python_lint_results(lint_results):
    readable_output = "Linting Results:\n"
    
    # Check if lint_results is empty
    if not lint_results:
        readable_output += "No linting results found.\n"
        return readable_output
    # Iterate through each lint result
    for result in lint_results:
        if isinstance(result, dict):
            # Extract details from the result
            line_no = result.get('line', 'N/A')
            column_no = result.get('column', 'N/A')
            message = result.get('message', 'N/A')
            symbol = result.get('symbol', 'N/A')
            result_type = result.get('type', 'N/A')

            # Append the formatted result to readable_output
            readable_output += f"  - {result_type.capitalize()} issue at Line {line_no}, Column {column_no}: {message} (symbol: {symbol})\n"
        else:
            readable_output += "  - Invalid lint result format.\n"

    return readable_output
    
def Python_Fix(script_name, input_path, error_path, fixed_path):
    print(f"[*]Fix Started for {input_path}")

    input_file = input_path
    error_file = os.path.join(error_path, script_name + '.err')
    fixed_file = os.path.join(fixed_path, script_name)
    
    # Read the original code from the input file
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            original_code = file.read()
            print(f"[*]File Available in {input_path}")
    except FileNotFoundError:
        logger.error(f"Error: {script_name} ::::: {input_file} file not found.")
        return

    print(f"[*]Lint Fix Started for {input_path}")


    result = subprocess.run(
          ["pylint", "--output-format=json", input_file],
          capture_output=True, text=True
        )
    

    
    # Ensure the directory exists before writing the error file
    os.makedirs(os.path.dirname(error_file), exist_ok=True)
    readable_output = parse_python_lint_results(json.loads(result.stdout))
    print(f"[*]Lint Errors Result Write Started for {input_path}")

    # Write the lint errors to the error file
    try:
        with open(error_file, "w") as file:
            file.write(readable_output)
        logger.info(f"Errors written to {error_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing errors to {error_file}: {e}")

    print(f"[*]Lint Errors Result Write Completed for {input_path}")

    print(f"[*]Processing Fix for {input_path}")

    # Get the fixed Code
    fixed_code = generate_fixed_python_code(readable_output, original_code)
    
    if fixed_code is None:
        return #stop the function if the code generation failed.
    
    print(f"[*]Fix Completed for {input_path}")

    # Ensure the directory exists before writing the fixed query file
    os.makedirs(os.path.dirname(fixed_file), exist_ok=True)
    
    # Write the fixed query to the file
    try:
        with open(fixed_file, "w", encoding="utf-8") as file:
            file.write(fixed_code.replace("```py", "").replace("```", ""))
        logger.info(f"Fixed code written to {fixed_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing fixed query to {fixed_file}: {e}")
    
# Argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files with linting and fix the code.")
    #parser.add_argument("script_name", help="Name of the script being processed.")
    parser.add_argument("changed_files", nargs='+', help="Path to the input file(s).")
    parser.add_argument("error_path", help="Path to the output error file.")
    parser.add_argument("fixed_path", help="Path to the output fixed file.")
    args = parser.parse_args()

    # Process each file in the input_path list
    for input_file in args.changed_files:
        script_name = os.path.basename(input_file) #Get the filename.
        Python_Fix(script_name, input_file, args.error_path, args.fixed_path)
