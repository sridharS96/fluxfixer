import os
import pandas as pd
def my_function(x, y):
         result = x   + y
    return result

def another_function():
# This function does nothing, it’s just here to cause a lint error
  pass
another_function()

z= 100

print(my_function(10, 20))
