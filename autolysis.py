# a function to create an analysis

#!/usr/bin/env uv
# uv: dependencies = ["pandas", "numpy", "os","seaborn"]


import pandas as pd
import numpy as np
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt


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
print (n_rows,n_cols)

variables=np.array(df.columns) # names of the variables

# understanding the types of variables & missing values

dtypes = pd.DataFrame(df.dtypes).reset_index()  
dtypes.columns = ['variable', 'data_type']  
missing_data=pd.DataFrame(df.isnull().sum()).reset_index()
missing_data=missing_data.rename(columns={'index':'variable'})
dtypes=pd.merge(dtypes,missing_data,on='variable')
dtypes.columns=['variable','data_type','missing_data']

# segregating the numeric and categorical variables

num_var=df.select_dtypes(include=['number'])
cat_var=df.select_dtypes(include=['object'])

# correlation map for the numerical variables

df_corr=num_var.corr()
df_corr_mask=df_corr.mask(np.equal(*np.indices(df_corr.shape)))

max_corr = df_corr_mask.abs().max().max() # fining the max correlation value
row_max, col_max = df_corr_mask[df_corr_mask.abs() == max_corr].stack().idxmax()


  
# 4 create a README.md file
with open(os.path.join(new_dir,'README.md'), 'w') as f:
    f.write(f"# Analysis Summary for {file_name}.csv\n\n")
    
    f.write(f"The dataset conatins {n_rows} samples with {n_cols} variables each\n\n")
    #f.write(f"the number of variables in the dataset:{n_cols} \n\n")

    f.write("the summary is the datatypes and number of missing values is as below\n\n")

    f.write(dtypes.to_markdown(index=False))

    f.write(f"\n\nThe variables with the highest correlation are: {row_max} and {col_max}, with a correlation of {round(max_corr,2)}\n\n")

# 5 create key charts

plots = []

# correlation heat map

plt.figure(figsize=(10, 8))
sns.heatmap(
    df_corr,
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(220,10,as_cmap=True),
    square=True,
    annot=True,fmt=".2f"
)
plt.title("correlation between the numeric variables \n",fontsize=28)
corr_heatmap_path=os.path.join(new_dir,"corr_heatmap.png")
plt.savefig(corr_heatmap_path)
plt.close()
plots.append(corr_heatmap_path)

# categorical variable pie charts


import math
ntot=len(cat_var.columns)
cols=math.ceil(math.sqrt(ntot))
rows=math.ceil(ntot/cols)

fig,axes=plt.subplots(rows,cols,figsize=(15,15))

if ntot == 1:
    axes = [axes]
else:
  axes=axes.flatten()

for i,col in enumerate(cat_var.columns):
    
    data = cat_var[col].value_counts(dropna=False)
    top5 = data.head(5)
    rest = data.iloc[5:].sum() 

    plot_data=pd.concat([top5, pd.Series([rest], index=['rest'])])


    sns.set_palette("pastel")
    wedges, texts, autotexts = axes[i].pie(plot_data, labels=plot_data.index, autopct='%1.1f%%', wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'})
    axes[i].set_title(col)
    axes[i].set_ylabel('')

if len(cat_var.columns) < len(axes):
    for j in range(len(cat_var.columns), len(axes)):
        fig.delaxes(axes[j])

plt.title("distribution of the categorical variables \n",fontsize=28)
plt.tight_layout()


cat_pie_path=os.path.join(new_dir,"cat_pie.png")
plt.savefig(cat_pie_path)
plt.close()
plots.append(cat_pie_path)

# numerical variable histograms

tot_num=len(num_var.columns)
cols_num=math.ceil(math.sqrt(tot_num))
rows_num=math.ceil(tot_num/cols_num)

fig,axes=plt.subplots(rows_num,cols_num,figsize=(15,15))

if tot_num == 1:
    axes = [axes]
else:
  axes=axes.flatten()

for i,col in enumerate(num_var.columns):
    sns.histplot(num_var[col], bins=15, ax=axes[i],kde=True)
    axes[i].set_title(col)
    axes[i].set_ylabel('')

for j in range(len(num_var.columns), len(axes)):
    fig.delaxes(axes[j])

plt.title("distribution of the numerical variables \n",fontsize=28)
plt.tight_layout()


num_hist_path=os.path.join(new_dir,"num_hist.png")
plt.savefig(num_hist_path)
plt.close()
plots.append(num_hist_path)