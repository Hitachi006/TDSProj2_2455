# a function to create an analysis

#!/usr/bin/env uv
# uv: dependencies = ["pandas", "numpy", "os"]


import pandas as pd
import numpy as np
import os
import sys


# 1 extract filename
file_path="".join(sys.argv[1:])
file_name=os.path.splitext(os.path.basename(file_path))[0]

# 2 create a new directory with filename
new_dir = os.path.join(os.getcwd(), file_name)
print(new_dir)
print(file_path)
os.makedirs(new_dir, exist_ok=True)
  
# 3 Perform an automated analysis and create a README file
df1=pd.read_csv(file_path,encoding='latin-1')
df1_anal=df1.describe()

  
# 4 create a README.md file
with open(os.path.join(new_dir,'README.md'), 'w') as f:
    f.write(df1_anal.to_markdown())

#print(f)

  
  

