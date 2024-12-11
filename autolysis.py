# a function to create an analysis

#!/usr/bin/env uv
# uv: dependencies = ["pandas", "numpy", "os"]


import pandas as pd
import numpy as np
import os
import sys


# 1 extract filename

file_path="".join(sys.argv[1:]) #
file_name=os.path.splitext(os.path.basename(file_path))[0]

# 2 create a new directory with filename
new_dir = os.path.join(os.getcwd(), file_name)
print(new_dir)
print(file_path)
os.makedirs(new_dir, exist_ok=True)
  
# 3 Perform an automated generic analysis

df=pd.read_csv(file_path,encoding='latin-1')

# describing the data

n_rows=df.shape[0] # how many samples ?
n_cols=df.shape[1] # how many variables?

variables=np.array(df.columns) # names of the variables

# understanding the types of variables & missing values
dtypes = pd.DataFrame(df.dtypes).reset_index()  
dtypes.columns = ['variable', 'data_type']  
missing_data=pd.DataFrame(df.isnull().sum()).reset_index()
missing_data=missing_data.rename(columns={'index':'variable'})
dtypes=pd.merge(dtypes,missing_data,on='variable')
dtypes.columns=['variable','data_type','missing_data']

  
# 4 create a README.md file
with open(os.path.join(new_dir,'README.md'), 'w') as f:
    f.write(f"# Data Summary for {file_name}\n\n")
    
    f.write("## Basic Information\n")

    f.write("# the dataset has {n_rows} samples with {n_columns} variables each\n\n")
    f.write("# the summary is the datatypes and number of missing values is as below\n\n")

    f.write(dtypes.to_markdown(index=False))

#print(f)

  
  

