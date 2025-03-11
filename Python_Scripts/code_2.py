"""This is a sample Python file with linting issues."""

import os, sys  # Unused import (W0611)

def BadFunctionName():  # Invalid function name (C0103)
x =  5  # Bad indentation (W0311), multiple spaces around operator (C0326)

class myClass:  # Class name should be PascalCase (C0103)
  def __init__(self, param1, param2):  # Bad indentation (W0311)
    self.param1=param1 # Missing space around operator (C0326)
    self.param2= param2  # Extra space (C0326)
    
  def bad_method(self):  # Method name should be in snake_case (C0103)
    if self.param1>0:print("Positive")  # No space around operator (C0326), multiple statements on one line (C0321)
    else: print("Negative")  # Multiple statements on one line (C0321)

def unused_function():  # Unused function (W0612)
    pass

# Generate 200 lines with errors
for i in range(20):
    print(f"""def func_{i}():
    print('This is function {i}')
    for j in range(5):
        if j%2==0:print('Even')  # Inline statement issue (C0321)
        else:print('Odd')  # Inline statement issue (C0321)
    """)

""" Unused variable, trailing whitespace  """   # Trailing whitespace (C0303)
variable_with_trailing_spaces = "Hello"    
