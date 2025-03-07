import os
import subprocess
import logging
import argparse
import configparser

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_sql_files(changed_files, error_path, fixed_path, script_path):
    try:
        if not os.path.exists(error_path):
            os.makedirs(error_path)
        if not os.path.exists(fixed_path):
            os.makedirs(fixed_path)

        for filename in changed_files:
            if filename.endswith(".sql"):
                try:
                    subprocess.run(["python", "-Xfrozen_modules=off", script_path, filename, error_path, fixed_path], check=True)
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
    print( f"Executes 'git diff --name-only' and returns a list of changed SQL files in the repository: {local_repo}")
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

    # Capture the variables from the config
    local_repo = config.get("Paths", "local_repo")
    script_path = config.get("Paths", "script_path")
    error_path = config.get("Paths", "error_path")
    fixed_path = config.get("Paths", "fixed_path")

    # Pass the captured variables to the functions
    changed_sql_files = get_changed_sql_files_from_git_diff(local_repo)
    process_sql_files(changed_sql_files, error_path, fixed_path, script_path)

if __name__ == "__main__":
    main()