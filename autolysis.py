# a function to create an analysis

#!/usr/bin/env uv
# uv: dependencies = ["pandas", "numpy", "os","seaborn"]


import pandas as pd
import numpy as np
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt

# 1 create a new directory with filename

def create_new_dir(file_name):
    new_dir = os.path.join(os.getcwd(), file_name)
    #print(new_dir)
    #print(file_path)
    os.makedirs(new_dir, exist_ok=True)
    return new_dir
  
# 2 Perform an automated generic analysis

def auto_gen_analysis(file_path):
    df=pd.read_csv(file_path,encoding='latin-1')

    # describing the data

    n_rows=df.shape[0] # how many samples ?
    n_cols=df.shape[1] # how many variables?
    #print (n_rows,n_cols)

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

    anal_sum={
                "n_samples":n_rows,
                "n_variables":n_cols,
                "var_dets":dtypes.to_dict(),
                "num_var":num_var,
                "cat_var":cat_var,
                "corr_matrix":df_corr.to_dict(),
                "max_corr_1":row_max,
                "max_corr_2":col_max,
                "max_corr":round(max_corr,2)
            }
   
    return anal_sum,df_corr_mask,df_corr,dtypes
  
# 3 create a README.md file

def read_me(new_dir,file_name,anal_sum,dtypes):
    
    with open(os.path.join(new_dir,'README.md'), 'w') as f:
       
        f.write(f"# Analysis Summary for _{file_name}.csv_\n\n")

        f.write(f"* The dataset contains **{anal_sum['n_samples']}** samples with **{anal_sum['n_variables']} variables** each\n\n")
        
        f.write(f"* Of the {anal_sum ['n_variables']} variables, **{len(anal_sum ['num_var'].columns)} are numeric variables** while **{len(anal_sum ['cat_var'].columns)} are categorical variables** \n\n")

        f.write("* The summary is the datatypes and number of missing values is as below\n\n")

        f.write(dtypes.to_markdown(index=False))

        f.write(f"\n\n > The variables with the highest correlation are: **{anal_sum['max_corr_1']}** and **{anal_sum['max_corr_2']}**, with a correlation of _{anal_sum['max_corr']}_\n\n")

    return f

# 4 create key charts

def key_charts(df_corr_mask,new_dir,anal_sum):
    
    plots = []

    # correlation heat map

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        df_corr_mask,
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
    ntot=len(anal_sum['cat_var'].columns)
    cols=math.ceil(math.sqrt(ntot))
    rows=math.ceil(ntot/cols)

    fig,axes=plt.subplots(rows,cols,figsize=(15,15))

    if ntot == 1:
        axes = [axes]
    else:
        axes=axes.flatten()

    for i,col in enumerate(anal_sum['cat_var'].columns):
    
        data = anal_sum['cat_var'][col].value_counts(dropna=False)
        top5 = data.head(5)
        rest = data.iloc[5:].sum() 

        plot_data=pd.concat([top5, pd.Series([rest], index=['rest'])])


    sns.set_palette("pastel")
    wedges, texts, autotexts = axes[i].pie(plot_data, labels=plot_data.index, autopct='%1.1f%%', wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'})
    axes[i].set_title(col)
    axes[i].set_ylabel('')

    if len(anal_sum['cat_var'].columns) < len(axes):
        for j in range(len(anal_sum['cat_var'].columns), len(axes)):
            fig.delaxes(axes[j])

    plt.title("distribution of the categorical variables \n",fontsize=28)
    plt.tight_layout()


    cat_pie_path=os.path.join(new_dir,"cat_pie.png")
    plt.savefig(cat_pie_path)
    plt.close()
    plots.append(cat_pie_path)

    # numerical variable histograms

    tot_num=len(anal_sum ['num_var'].columns)
    cols_num=math.ceil(math.sqrt(tot_num))
    rows_num=math.ceil(tot_num/cols_num)

    fig,axes=plt.subplots(rows_num,cols_num,figsize=(15,15))

    if tot_num == 1:
        axes = [axes]
    else:
      axes=axes.flatten()

    for i,col in enumerate(anal_sum ['num_var'].columns):
        sns.histplot(anal_sum ['num_var'][col], bins=15, ax=axes[i],kde=True)
        axes[i].set_title(col)
        axes[i].set_ylabel('')

    for j in range(len(anal_sum ['num_var'].columns), len(axes)):
        fig.delaxes(axes[j])

    plt.title("distribution of the numerical variables \n",fontsize=28)
    plt.tight_layout()


    num_hist_path=os.path.join(new_dir,"num_hist.png")
    plt.savefig(num_hist_path)
    plt.close()
    plots.append(num_hist_path)

    return plots

# 5 function to get LLM feedback



# 6 function to string the steps together into the main code 

def main():

    # 0 extract filename and file path from the system command

    csv_path="".join(sys.argv[1:]) #
    csv_name=os.path.splitext(os.path.basename(csv_path))[0]

    # 1 create a new directory with filename using the defined function
    new_directory= create_new_dir(csv_name)

    # 2 perform automated analysis using the defined function
    anlsys_sum,corr_mask,corr_mat,data_types=auto_gen_analysis(csv_path)

    # 3 write a readme file using the defined function
    readme=read_me(new_directory,csv_name,anlsys_sum,data_types)

    # 4 build key charts using the defined function
    charts=key_charts(corr_mask,new_directory,anlsys_sum)

    # 5 get LLM feedback using the defined function


# code execution block
if __name__=="__main__":
    main()