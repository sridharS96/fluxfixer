#FluxFixer

#config.ini
#######################################################################################################
[Paths]
full_check = Y

fluff_config = <<Local_Path>>\fluxfixer\py_Scripts\sqlfluff.ini    ---> sqlfluff config

local_repo = <<Local_Path>>\fluxfixer

script_path = <<Local_Path>>\fluxfixer\py_Scripts\code_run_arg.py

error_path = <<Local_Path>>\fluxfixer\SQl_full_test\SQL\errors

fixed_path = <<Local_Path>>\fluxfixer\SQl_full_test\SQL\fixed

#######################################################################################################


#sqlfluff.ini
#######################################################################################################
[sqlfluff]
dialect = BigQuery

exclude_rules =  LT04, LT02, ST06

max_line_length = 120

templater = jinja

#######################################################################################################
