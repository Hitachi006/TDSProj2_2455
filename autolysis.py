# a function to create an analysis

#!/usr/bin/env uv
# uv: dependencies = ["pandas", "numpy", "os"]


import pandas as pd
import numpy as np
import os
import sys


# 1 extract filename
file_name="".join(sys.argv[1:]).split('.')[0]

# 2 create a new directory with filename
new_dir = os.path.join(os.getcwd(), file_name)
#print(new_dir)
os.makedirs(new_dir, exist_ok=True)
  
# 3 Perform an automated analysis and create a README file
df=pd.read_csv('goodreads.csv')
df_anal=df.describe()
  
# 4 create a README.md file
with open(os.path.join(new_dir,'README.md'), 'w') as f:
 f.write(df_anal.to_markdown())

print(f)

  
  

