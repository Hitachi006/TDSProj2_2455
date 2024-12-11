# a function to create an analysis

#///script
#dependencies = ["pandas","numpy","os"]
#///

#import pandas as pd
#import numpy as np
#import os
import sys


def create_dir(file_path):
  # 1 extract filename
  file_name=os.path.splitext(os.path.basename(file_path)[0])

  # 2 create a new directory with filename
  new_dir = os.path.join(os.getcwd(), file_name)
  os.makedirs(new_dir, exist_ok=True)
  
  # 3 Perform an automated analysis and create a README file
  df=pd.read_csv(file_path)
  df_anal=df.describe()
  
  # 4 create a README.md file
     
  with open(os.path.join(new_dir,'README.md'), 'w') as f:
    f.write(df_anal.to_markdown())

  return(f)

  
  

