import os
import subprocess
import logging
import argparse
import configparser

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_json_files(changed_files, json_error_path, json_fixed_path, script_path):
    try:
        if not os.path.exists(json_error_path):
            os.makedirs(json_error_path)
        if not os.path.exists(json_fixed_path):
            os.makedirs(json_fixed_path)

        for filename in changed_files:
            if filename.endswith(".json"):
                try:
                    subprocess.run(["python", "-Xfrozen_modules=off", script_path, filename, json_error_path, json_fixed_path], check=True)
                    print(f"Successfully processed: {filename}")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Error processing {filename}: {e}")
                except FileNotFoundError as e:
                    logger.error(f"Error: JSON script not found at {script_path}: {e}")
                    return  # stop the function if the script is not found.
                except Exception as e:
                    logger.error(f"An unexpected error occurred while processing {filename}: {e}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        


def process_python_files(changed_files, python_error_path, python_fixed_path, script_path):
    try:
        if not os.path.exists(python_error_path):
            os.makedirs(python_error_path)
        if not os.path.exists(python_fixed_path):
            os.makedirs(python_fixed_path)

        for filename in changed_files:
            if filename.endswith(".py") and "Python_Scripts" in filename:
                try:
                    subprocess.run(["python", "-Xfrozen_modules=off", script_path, filename, python_error_path, python_fixed_path], check=True)
                    print(f"Successfully processed: {filename}")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Error processing {filename}: {e}")
                except FileNotFoundError as e:
                    logger.error(f"Error: Python script not found at {script_path}: {e}")
                    return  # stop the function if the script is not found.
                except Exception as e:
                    logger.error(f"An unexpected error occurred while processing {filename}: {e}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        
 

def process_sql_files(changed_files, SQL_error_path, SQL_fixed_path, script_path,config=None):
    try:
        if not os.path.exists(SQL_error_path):
            os.makedirs(SQL_error_path)
        if not os.path.exists(SQL_fixed_path):
            os.makedirs(SQL_fixed_path)

        for filename in changed_files:
            if filename.endswith(".sql"):
                try:
                    print("python", "-Xfrozen_modules=off", script_path, filename, f"--config={config}")
                    command = ["python", "-Xfrozen_modules=off", script_path, filename, SQL_error_path, SQL_fixed_path, config]
                    subprocess.run(command, check=True)
                    print(f"Successfully processed: {filename}")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Error processing {filename}: {e}")
                except FileNotFoundError as e:
                    logger.error(f"Error: Python script not found at {script_path}: {e}")
                    return  # stop the function if the script is not found.
                except Exception as e:
                    logger.error(f"An unexpected error occurred while processing {filename}: {e}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        
def get_changed_files_from_git_diff(local_repo):
    print( f"Executes 'git diff --name-only' and returns a list of changed files in the repository: {local_repo}")
    try:
        os.chdir(local_repo)
        result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True)
        git_diff_output = result.stdout
        changed_files = []
        changed_SQL_files = []
        changed_python_files = []
        changed_json_files = []
        print(f"List of Updated Files:\n{git_diff_output}")
        
        # Getting the SQL Files
        for line in git_diff_output.splitlines():
            if line.endswith(".sql"):
                changed_SQL_files.append(line.strip())
        print(f"Changed SQL files:{changed_SQL_files}")
        changed_files.append(changed_SQL_files)
        
        # Getting the Python Files
        for line in git_diff_output.splitlines():
            if line.endswith(".py") and "Python_Scripts" in line:
                changed_python_files.append(line.strip())
        print(f"Changed Python files:{changed_python_files}")
        changed_files.append(changed_python_files)
        
        # Getting the JSON Files
        for line in git_diff_output.splitlines():
            if line.endswith(".json"):
                changed_json_files.append(line.strip())
        print(f"Changed JSON files:{changed_json_files}")
        changed_files.append(changed_json_files)
        
        return changed_files
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing git diff: {e}")
        return []
    except FileNotFoundError as e:
        logger.error(f"Error: Git repository not found: {e}")
        return []
        
def get_all_sql_files(folder_path):
    print(f"Getting all SQL files from: {folder_path}")
    sql_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".sql"):
                sql_files.append(os.path.join(root, file))
    print(f"Found SQL files: {sql_files}")
    return sql_files

def get_all_python_files(folder_path):
    print(f"Getting all python files from: {folder_path}")
    python_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py") and "Python_Scripts" in file:
                python_files.append(os.path.join(root, file))
    print(f"Found python files: {python_files}")
    return python_files
    
def get_all_json_files(folder_path):
    print(f"Getting all json files from: {folder_path}")
    json_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    print(f"Found json files: {json_files}")
    return json_files

def load_config(config_file):
    print(f"Loading config from: {os.path.abspath(config_file)}")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        #print(f"Raw config content:\n{content}")
        config = configparser.ConfigParser()
        config.read(config_file)
        #print(f"Config sections: {config.sections()}")
        print(f"Config Parsed successfully.")
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        return configparser.ConfigParser()

def main():
    parser = argparse.ArgumentParser(description="Process changed SQL files.")
    parser.add_argument("--config", default="config.ini", help="Path to the configuration file.")
    args = parser.parse_args()

    config = load_config(args.config)
    
    print("--------------------------Config File Read Started--------------------------------------")

    # Capture the variables from the config
    local_repo = config.get("Paths", "local_repo")
    SQL_script_path = config.get("Paths", "SQL_script_path")
    SQL_error_path = config.get("Paths", "SQL_error_path")
    SQL_fixed_path = config.get("Paths", "SQL_fixed_path")
    python_script_path = config.get("Paths", "python_script_path")
    python_error_path = config.get("Paths", "python_error_path")
    python_fixed_path = config.get("Paths", "python_fixed_path")
    json_script_path = config.get("Paths", "json_script_path")
    json_error_path = config.get("Paths", "json_error_path")
    json_fixed_path = config.get("Paths", "json_fixed_path")
    sql_fix_config = config.get("Paths", "SQL_config")
    python_fix_config = config.get("Paths", "python_config")
    python_fix_config = config.get("Paths", "json_config")
    full_check = config.get("Paths", "full_check")

    

    
    
    print("------------------------Config File Path Extraction Completed-------------------------------")


    print("-----------------Process Started to get List of Updated Files-------------------------------")


    if full_check == "Y":
        changed_sql_files = get_all_sql_files(local_repo)
        changed_python_files = get_all_sql_files(local_repo)
        changed_json_files = get_all_sql_files(local_repo)

    else:
        changed_files = get_changed_files_from_git_diff(local_repo)
        changed_sql_files =  changed_files[0]
        changed_python_files = changed_files[1]
        changed_json_files = changed_files[2]
    
    print("-----------------Process to get List of Updated Files Completed-----------------------------")

    print("----------------------------SQL Fix Started------------------------------------------------")
    
    print(f"Processing {len(changed_sql_files)} SQL files...")
    #process SQL Files
    process_sql_files(changed_sql_files, SQL_error_path, SQL_fixed_path, SQL_script_path,sql_fix_config)
    
    print("----------------------------SQL Fix Completed----------------------------------------------")

    print("---------------------------Python Fix Started--------------------------------------------")
    print(f"Processing {len(changed_python_files)} python files...")

    #process Python Files
    process_python_files(changed_python_files, python_error_path, python_fixed_path, python_script_path)
    
    print("---------------------------JSON Fix Started--------------------------------------------")
    print(f"Processing {len(changed_json_files)} json files...")

    #process JSON Files
    process_json_files(changed_json_files, json_error_path, json_fixed_path, json_script_path)
    
    print("---------------------------JSON Fix Completed--------------------------------------------")


if __name__ == "__main__":
    main()
