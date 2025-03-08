import os
import subprocess
import logging
import argparse
import configparser

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_sql_files(changed_files, error_path, fixed_path, script_path,fluff_config):
    try:
        if not os.path.exists(error_path):
            os.makedirs(error_path)
        if not os.path.exists(fixed_path):
            os.makedirs(fixed_path)

        for filename in changed_files:
            if filename.endswith(".sql"):
                try:
                    print("python", "-Xfrozen_modules=off", script_path, filename, f"--config={fluff_config}")
                    command = ["python", "-Xfrozen_modules=off", script_path, filename, error_path, fixed_path, fluff_config]
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

def get_changed_sql_files_from_git_diff(local_repo):
    print(f"Executes 'git diff --name-only' and returns a list of changed SQL files in the repository: {local_repo}")
    try:
        os.chdir(local_repo)
        result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True)
        git_diff_output = result.stdout
        changed_files = []
        print(f"Git diff output:\n{git_diff_output}")
        print(f"Changed files:{changed_files}")
        for line in git_diff_output.splitlines():
            if line.endswith(".sql"):
                changed_files.append(line.strip())
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

def load_config(config_file):
    print(f"Loading config from: {os.path.abspath(config_file)}")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        config = configparser.ConfigParser()
        config.read(config_file)
        print(f"Config Parsed successfully.")
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        return configparser.ConfigParser()

def main():
    parser = argparse.ArgumentParser(description="Process SQL files.")
    parser.add_argument("--config", default="config.ini", help="Path to the configuration file.")
    parser.add_argument("--full_check", action="store_true", help="Check all SQL files in the folder.")
    args = parser.parse_args()

    config = load_config(args.config)
    full_check = config.get("Paths", "full_check")
    local_repo = config.get("Paths", "local_repo")
    script_path = config.get("Paths", "script_path")
    error_path = config.get("Paths", "error_path")
    fixed_path = config.get("Paths", "fixed_path")
    fluff_config = config.get("Paths", "fluff_config")

    if full_check == "Y":
        sql_files = get_all_sql_files(local_repo)
    else:
        sql_files = get_changed_sql_files_from_git_diff(local_repo)

    print(f"Processing {len(sql_files)} files...")
    process_sql_files(sql_files, error_path, fixed_path, script_path,fluff_config)

if __name__ == "__main__":
    main()