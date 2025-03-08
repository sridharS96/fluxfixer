#FluxFixer

#config.ini --> Update these to point local file directory

  --> use full_check = Y to check all sql files in the folder & N for the only changed files after the repo cloned( git diff ).
  --> linter on the full_check or changed files. error file placed in error_path. fixed filed placed in fixed_path. and linter again runs on fixed_path.

#sqlfluff.ini --> contion configuration of sqlfluff

#run job in inside local repo fluxfixer\py_scripts
  python code_fix_run.py --config=config.ini

  #this calls the fluxfixer\py_Scripts\code_run_arg.py with details of script_name , error_file path, fixed file path.
  
