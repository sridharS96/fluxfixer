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

def parse_json_lint_results(lint_results):
    if not isinstance(lint_results, list):
        return "Invalid lint results format.\n"
    
    if not lint_results:
        return "Linting Results:\nNo linting issues found.\n"
    
    readable_output = "Linting Results:\n"
    for error in lint_results:
        error_type = error.get("error", "Unknown error")
        position = error.get("position", "N/A")
        message = error.get("message", "")
        
        if message:
            readable_output += f" - {error_type}: {message}\n"
        else:
            readable_output += f" - {error_type} at position {position}\n"
    
    return readable_output


def generate_fixed_json_code(lint_results, original_json):
    contents = f"""
      Given the following JSON data and its linting errors, modify the JSON to fix the issues:
       Original JSON:
       {original_json}
       
       Linting Errors:
       {lint_results}
       
       Your task is to:
       1. Correct all JSON syntax issues (missing braces, incorrect commas, invalid characters, etc.).
       2. Fix the specific errors reported in the linting results while maintaining the original structure.
       3. Ensure the JSON is well-formed, properly indented, and valid.
       4. Do not change the meaning or structure of the JSON unless required for fixing errors.
       5. Provide only the corrected JSON output with no explanations or extra text.
    """
    
    try:
        response = model.generate_content(contents)
        
        match = re.search(r'```json\n(.*?)```', response.text, re.DOTALL)
        
        fixed_json = match.group(1).strip()
        
        #json.loads(fixed_json)  # This will throw an exception if the JSON is invalid

    except Exception as e:
        logger.error(f"Error generating fixed JSON: {e}")
        return None  # Return None if there was an error generating the fixed code

    return fixed_json
    
# Function to fix JSON file
def Json_Fix(script_name, input_path, error_path, fixed_path):
    print(f"[*]Fix Started for {input_path}")

    input_file = input_path
    error_file = os.path.join(error_path, script_name + '.err')
    fixed_file = os.path.join(fixed_path, script_name)
    
    
    # Read the original JSON from the input file
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            original_json = file.read()
            print(f"[*]File Available in {input_path}")

    except FileNotFoundError:
        logger.error(f"Error: {script_name} ::::: {input_file} file not found.")
        return

    print(f"[*]Lint Fix Started for {input_path}")

    errors = []
    

    # Check for missing commas between key-value pairs
    missing_comma_pattern = re.compile(r'"\s*\w+\s*":\s*[^,\}\]]+\s*"\s*\w+\s*":')
    for match in missing_comma_pattern.finditer(original_json):
        errors.append({"error": "Possible missing comma", "position": match.start()})
    
    # Check for missing colons in key-value pairs
    missing_colon_pattern = re.compile(r'"\s*\w+\s*"\s*"\s*\w+\s*":')
    for match in missing_colon_pattern.finditer(original_json):
        errors.append({"error": "Possible missing colon", "position": match.start()})
    
    # Try loading JSON to catch structural errors
    try:
        json.loads(original_json)
    except json.JSONDecodeError as e:
        errors.append({"error": "JSON decoding error", "message": str(e)})
    
    
 
    print(f"[*]Lint Errors Result Write Started for {input_path}")

    # Ensure the directory exists before writing the error file
    os.makedirs(os.path.dirname(error_file), exist_ok=True)
    
    if len(errors)>0:
        # Parsing the errors returned by jsonlint
        readable_output = parse_json_lint_results(errors)
    else:
        readable_output = "No linting errors found."
    
    # Write the lint errors to the error file
    try:
        with open(error_file, "w") as file:
            file.write(readable_output)
        logger.info(f"Errors written to {error_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing errors to {error_file}: {e}")
    
    print(f"[*]Lint Errors Result Write Completed for {input_path}")

    print(f"[*]Processing Fix for {input_path}")

    # Get the fixed JSON code (make sure your function can generate valid JSON)
    fixed_json = generate_fixed_json_code(readable_output, original_json)
    
    if fixed_json is None:
        return  # Stop the function if the JSON fix generation failed.
        
    print(f"[*]Fix Completed for {input_path}")

    
    # Ensure the directory exists before writing the fixed JSON file
    os.makedirs(os.path.dirname(fixed_file), exist_ok=True)
    
    # Write the fixed JSON to the file
    try:
        with open(fixed_file, "w", encoding="utf-8") as file:
            file.write(fixed_json)
        logger.info(f"Fixed JSON written to {fixed_file} successfully.")
    except Exception as e:
        logger.error(f"Error writing fixed JSON to {fixed_file}: {e}")
    

# Argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files with linting and fix the code.")
   # parser.add_argument("script_name", help="Name of the script being processed.")
    parser.add_argument("changed_files", nargs='+', help="Path to the input file(s).")
    parser.add_argument("error_path", help="Path to the output error file.")
    parser.add_argument("fixed_path", help="Path to the output fixed file.")
    args = parser.parse_args()

    # Process each file in the input_path list
    for input_file in args.changed_files:
        script_name = os.path.basename(input_file) #Get the filename.
        Json_Fix(script_name, input_file, args.error_path, args.fixed_path)
