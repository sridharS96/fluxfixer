import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_sql_files(folder_path, script_path,error_file,fixed_path):
    """
    Finds all .sql files in the given folder and passes them to the specified Python script.

    Args:
        folder_path (str): The path to the folder containing the SQL files.
        script_path (str): The path to the Python script (abc.py).
    """
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".sql"):
                file_path = os.path.join(folder_path, filename)
                try:
                    # Execute the Python script with the SQL file path as an argument.
                    subprocess.run(["python" ,"-Xfrozen_modules=off", script_path,filename, file_path,error_file,fixed_path ], check=True)
                    print(f"Successfully processed: {file_path}")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Error processing {file_path}: {e}")
                except FileNotFoundError as e:
                    logger.error(f"Error: Python script not found at {script_path}: {e}")
                    return #stop the function if the script is not found.
                except Exception as e:
                    logger.error(f"An unexpected error occurred while processing {file_path}: {e}")

    except FileNotFoundError:
        logger.error(f"Error: Folder not found at {folder_path}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

# Example usage:
folder = r"SQL_Script\" # Replace with your folder path
script_path = r"py_Scripts\code_run_arg.py" # Replace with your script path
error_file = r"SQL_scripts\SQL\errors" # Replace with your error path 
fixed_file = r"SQL_scripts_SQL\SQL\fixed" # Replace with your fixed path
process_sql_files(folder, script_path,error_file,fixed_file)