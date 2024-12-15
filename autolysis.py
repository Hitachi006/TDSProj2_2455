# adeclaring uv inline dependencies
#!/usr/bin/env uv
# uv: dependencies = ['pandas','jason', 'scikit-learn' ,'numpy','sys','os','seaborn','matplotlib','requests','json','openai']


# 0.1 Key Imports
# -----------------------------------------------------------------------

from matplotlib import axis
import pandas as pd
import numpy as np
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt
#import requests
import json
import openai
from openai import OpenAI
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer,KNNImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import RobustScaler

# 0.2 configure the OpenAI API
# ----------------------------------------------------------------------

client=OpenAI(
    base_url='https://aiproxy.sanand.workers.dev/openai/v1',
    api_key=os.getenv("AIPROXY_TOKEN"),
)

# 1. Directory setup | dataset loading | EDA 
# ----------------------------------------------------------------------

# 1.1 create a new directory with filename
# ----------------------------------------------------------------------

def create_new_dir(file_name):
    new_dir = os.path.join(os.getcwd(), file_name)
    os.makedirs(new_dir, exist_ok=True)
    return new_dir
  
# 1.2 load the dataset and undertake exploratory data analysis
# ----------------------------------------------------------------------

def load_eda(file_path):
    
    # load the dataset
    # ------------------------------------------------------------------
    df=pd.read_csv(file_path,encoding='latin-1')

    # describing the data
    # ------------------------------------------------------------------

    n_rows=df.shape[0] # how many samples ?
    n_cols=df.shape[1] # how many variables?
    variables=np.array(df.columns) # names of the variables
    sample=df.head().to_dict() # data snippet for the llm

    # tabulating the name, types of variables & missing values
    # ------------------------------------------------------------------

    dtypes = pd.DataFrame(df.dtypes).reset_index()  
    dtypes.columns = ['variable', 'data_type']  
    missing_data=pd.DataFrame(df.isnull().sum()).reset_index()
    missing_data=missing_data.rename(columns={'index':'variable'})
    dtypes=pd.merge(dtypes,missing_data,on='variable')
    dtypes.columns=['variable','data_type','missing_data']


    # collecting all the outputs of the eda into a dictionary:
    # ------------------------------------------------------------------
    
    eda_sum={
                "n_samples":n_rows,
                "n_variables":n_cols,
                "var_dets":dtypes.to_dict(),
                #"num_var_desc":num_var_desc.to_dict(),
                #"cat_var_desc":cat_var_desc.to_dict(),
            }

    return eda_sum,sample,df

#1.3 identify specific variable types in the dataset - ask llm
# ----------------------------------------------------------------------

def ask_llm_var_input(eda_sum,sample):

    prompt=(f" this is a sample of my dataset : {sample}, key summary : {eda_sum}\n"
            f"1. If the dataset contains time series data, identify the name(s) of the date or time-related column(s) (e.g., a column with dates or timestamps).output names of the variables as an array of of strings. If no such column exists, return false, \n"
            f"2. based on the variable name, identify the variables with int or float datatype, that might represent strings or labels but not numeric values. e.g id numbers, order numbers.ratings are numeric values. output names of the variables as an array of of strings. if unsure, return empty array"
            f"3. identify the dependent variable in the dataset. if unsure, leave it blank" 
            )
    
    # note : the promt for now assumes single output/target variable i.e not some multi-class problem
   
    messages=[
                {"role": "system", "content": "You are an awesome data analyst assistant."},
                {"role": "user", "content": prompt}
            ]
    
    try:
        response =client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,
                    response_format={
                        "type":"json_schema",
                        "json_schema":{
                            "name":"dtype_id",
                            "schema": {
                                    "type":"object",
                                    "properties":{
                                    "date_var":{
                                        "type":"object",
                                        "properties":{
                                            "timeseries":{
                                                "type":"boolean",
                                                "description": "does the date type variable exist?",
                                                        },
                                            "date_var_name":{
                                                "type":"array",
                                                "items":{"type":"string"},
                                                "description": "name of datetime variable, if any",
                                                        },
                                                    },
                                            },
                                    
                                    "num_cats":{
                                        "type":"array",
                                        "items":{"type":"string"},
                                        "description":"list of names of numeric type variables that are strings or labels",
                                        },
                                    
                                    "dep_var":{
                                        "type":"string",
                                        "description":"name of the dependant variable",
                                            },
                                       }
                                    }
                                }}
                                )
        
        content = response.choices[0].message.content
        var_input=json.loads(content)
        is_timeseries=var_input['date_var']['timeseries']
        date_var_name=var_input['date_var']['date_var_name']
        label_var_list=var_input['num_cats']
        target_var=var_input['dep_var']
        return (var_input,is_timeseries,date_var_name,label_var_list,target_var)
        
    
    except Exception as e:
        print(f"Error interacting with LLM: {e}")
        return("No insights could be generated due to an error.")


# 2. data preparation
# ----------------------------------------------------------------------

# dropping label variables from the analysis set
# ------------------------------------------------------------------
def drop_labels(df,label_var_list):

    df_num_vars=df.select_dtypes(include=['number']).columns.to_list()
    label_drop_list=[]
    for i in label_var_list:
        if i in df_num_vars:
            label_drop_list.append(i)
    df_anal=df.drop(label_drop_list,axis=1)
    return(df_anal)


# seggregating the date variable out 
# ------------------------------------------------------------------

def cull_date_var(df_anal,date_var_name):
    
    date_var=df_anal[date_var_name] # dataframe containing the date variable(s)
    df_anal.drop(date_var_name,axis=1)

    return(date_var,df_anal)

# seggregating the "X" & "y"
# ------------------------------------------------------------------

def data_prep_X_y(df_anal,target_variable):

    y=df_anal[target_variable]
    X=df_anal.drop([target_variable],axis=1)
    return(X,y)

def data_prep_X(df_anal):
    X=df_anal
    y=[]
    return(X,y)

# preprocessing the "X" variables
# ------------------------------------------------------------------

def data_preprocess(X):

    # seggregating the numeric,categorical,datetype into seperate lists 
    # ------------------------------------------------------------------

    num_var=X.select_dtypes(include=['number']) # dataframe containing the numeric variables
    cat_var=X.select_dtypes(include=['object']) # dataframe containing the categorical variables
    
    num_var_desc=num_var.describe() # statistical summary of the numerical variables
    cat_var_desc=cat_var.describe() # statistical summary of the categorical vriables
    
    # scaling the numeric variables and encoding the categorical variables using a pipeline
    # -----------------------------------------------------------------------------------
    
    cat_enc=Pipeline(steps=[
               ('imputer',SimpleImputer(strategy='constant',fill_value='unknown')),
               ('encoder',OneHotEncoder(handle_unknown='ignore',drop='if_binary',sparse_output=False))
             ])

    num_scale=Pipeline(steps=[
               ('imputer',SimpleImputer(strategy='median')),
               ('scaler',RobustScaler())
             ])
    
    ct=ColumnTransformer(
        [
            ("cat_enc",cat_enc,cat_var.columns.to_list()),
            ("num_scale",num_scale,num_var.columns.to_list())
        ],remainder="passthrough",verbose=False,verbose_feature_names_out=False).set_output(transform='pandas')
    
    X_trans=ct.fit_transform(X)
    num_var_trans=num_scale.fit_transform(num_var)

    return(num_var,cat_var,
           num_var_desc,cat_var_desc,
           X_trans,num_var_trans)

# 3. Data Analysis
# ----------------------------------------------------------------------

#3.1 correlation of the numerical variables
# ----------------------------------------------------------------------

def corr_anal(num_var):
    df_corr=num_var.corr()
    df_corr_mask=df_corr.mask(np.equal(*np.indices(df_corr.shape)))
    max_corr = df_corr_mask.abs().max().max() # fining the max correlation value
    row_max, col_max = df_corr_mask[df_corr_mask.abs() == max_corr].stack().idxmax()
    corr_sum={"corr_matrix":df_corr.to_dict(),
                "max_corr_1":row_max,
                "max_corr_2":col_max,
                "max_corr":round(max_corr,2)
                }
    return(corr_sum,df_corr_mask)


# 4 Define Visualizations
# -----------------------------------------------------------------------

# 4.1 Set common styling settings for all Seaborn plots
# -----------------------------------------------------------------------
def set_common_styling():
    sns.set_theme(style="whitegrid")  # Use a grid-based theme
    plt.rcParams.update({
        'figure.figsize': (10, 6),  # Set default figure size
        'axes.titlesize': 12,  # Set title font size
        'axes.labelsize': 8,  # Set label font size
        'xtick.labelsize': 8,  # Set x-tick font size
        'ytick.labelsize': 8,  # Set y-tick font size
        'legend.fontsize': 8  # Set legend font size
    })

# 4.2 correlation heat map
# -----------------------------------------------------------------------
def plot_heatmap(data,new_dir):
    
    plt.figure()
    sns.heatmap(
        data,
        vmin=-1, vmax=1, center=0,
        cmap=sns.diverging_palette(220,10,as_cmap=True),
        linecolor='white',
        linewidths=0.05,
        square=True,
        annot=True,fmt=".2f"
            )
    plt.title("correlation between the numeric variables \n\n",fontsize=15)
    corr_heatmap_path=os.path.join(new_dir,"corr_heatmap.png")
    plt.savefig(corr_heatmap_path)
    plt.close()
    return(corr_heatmap_path)

# 4.2 Frequency histogram
# -----------------------------------------------------------------------

def plot_histogram(data, column,bins,new_dir):
    
    plt.figure()
    sns.histplot(data[column], bins=bins, kde=True)
    plt.title(f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    

    plt.title("frequency count of {column}\n\n",fontsize=15)
    histogram_path=os.path.join(new_dir,"histogram.png")
    plt.savefig(histogram_path)
    plt.close()
    return(histogram_path)

# 4.3 Scatter Plot
# -----------------------------------------------------------------------

def plot_scatter(new_dir,data,x,y,hue):
    plt.figure()  # Create a new figure for this plot
    sns.scatterplot(data=data, x=x, y=y, hue=hue)
    plt.title(f"Scatter Plot: {x} vs {y}")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.legend(title=hue)

    plt.title("scatter plot of {x} vs {y} \n\n",fontsize=15)
    scatter_path=os.path.join(new_dir,"scatter.png")
    plt.savefig(scatter_path)
    plt.close()
    return(scatter_path)

# 4.4 Box Plot
# -----------------------------------------------------------------------

def plot_box(data,new_dir):
    fig, ax = plt.subplots()   # Create a new figure for this plot
    sns.boxplot(data=data,log_scale=True)
    plt.title(f"Box Plot")
    ax.tick_params(axis='x',labelrotation=45,labelsize=8) 
    

    plt.title("box plot of {x} vs {y} \n\n",fontsize=15)
    box_path=os.path.join(new_dir,"box.png")
    plt.savefig(box_path)
    plt.close()
    return(box_path)

# 4.5 Pair-wise plot
# -----------------------------------------------------------------------

def plot_pairs(data, new_dir):
    plt.figure()  # Create a new figure for this plot
    sns.pairplot(data,diag_kind="kde", markers=["o", "s", "D"])
    plt.suptitle("Pairwise Plot", y=1.02)  # Adjust title position
    
    plt.title("pair_plot \n\n",fontsize=15)
    pair_path=os.path.join(new_dir,"pair.png")
    plt.savefig(pair_path)
    plt.close()
    return(pair_path)




# 6 ask llm to write an analysis summary 
# --------------------------------------------------------------------

def ask_llm_summary(anlsys_list):

    prompt=(f" I have created an analysis of a csv dataset {anlsys_list}\n"
            f"please summairize the analysis in the following structure:\n"
            f"1. Describe the possible context of the dataset \n"
            f"2. Note down the key observations from teh exploratory data analysis \n"
            f"2. explain the analysis carried out  \n"
            f"3. call out the key insights from the analysis done \n"
            f"4. recommend potential implications of the insights \n"
            )
   
    messages=[
                {"role": "system", "content": "You are an awesome data analyst assistant."},
                {"role": "user", "content": prompt}
            ]

    
    try:
        response =client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                    )
        content=response.choices[0].message.content
        return(content)
        
    
    except Exception as e:
        print(f"Error interacting with LLM: {e}")
        return "No insights could be generated due to an error."

# 6 create a README.md file
# --------------------------------------------------------------------

def read_me(new_dir,file_name,content):
    
    with open(os.path.join(new_dir,'README.md'), 'w') as f:
       
        f.write(f"# Analysis Summary for _{file_name}.csv_\n\n")

        f.write(content)
        
        
    return f   

# 7 function to string the steps together into the main code 
# --------------------------------------------------------------------

def main():

        
    # A. extract filename and file path from the system command

    csv_path="".join(sys.argv[1:]) #
    csv_name=os.path.splitext(os.path.basename(csv_path))[0]

    # B. create a new directory with filename using the defined function
    new_directory= create_new_dir(csv_name)

    # C. perform basic EDA
    explore_sum,snip,df_main=load_eda(csv_path)

    # D. ask llm inputs related to variables and datatypes
    llm_var_input,is_ts,date_col_name,label_col_list,tgt_var=ask_llm_var_input(explore_sum,snip)
    

    
    # E. Prepare the data for the analysis
    
    df_for_anal=df_main # replicating the dataset for modifications

    if len(label_col_list)>0:
        df_for_anal= drop_labels(df_for_anal,label_col_list)
    
    if is_ts==True:
        date_var_col,df_for_anal=cull_date_var(df_for_anal,date_col_name)
    
    
    if tgt_var!="":
        X_anal,y_anal=data_prep_X_y(df_for_anal,tgt_var)
    else:
        X_anal,y_anal=data_prep_X(df_for_anal)
    
    X_anal=df_for_anal
    num_var_df,cat_var_df,num_var_dscr,cat_var_dscr,X_anal_tf,num_var_df_tf=data_preprocess(X_anal)

    # F. data analysis
    
    corr_summary,corr_mask=corr_anal(num_var_df)

    
      
   # G create charts

    plots=[]
    
    #Chart 1
    corr_heatmap=plot_heatmap(corr_mask,new_directory)
    plots.append(corr_heatmap)

    
    #Chart 2
    x=num_var_df_tf.columns
    y=num_var_df_tf.values
    box_path=plot_box(num_var_df,new_directory)

    plots.append(box_path)
    
    #Chart 3
    x1=corr_summary['max_corr_1']
    x2=corr_summary['max_corr_2']
    #max_corr_pair=pd.concat([x1,x2])
    pair_path=plot_pairs(num_var_df,new_directory)
    plots.append(pair_path)

    '''
    #Chart 4

    hist_path=plot_histogram(num_var_df,new_directory)
    plots.append(hist_path)

    '''

    #H collate all the analysis pieces into a dict

    analysis={
                "eda": explore_sum,
                "sample data": snip,
                "llm early fb": llm_var_input,
                "statistical summary": [num_var_dscr.to_dict(),cat_var_dscr.to_dict()],
                "key analysis": corr_summary
            }
    
    
    
    

    # 5 get LLM to provide the feedback
    
    llmfeedback=ask_llm_summary(analysis)

    # 6 Create a readme file and write the narrative
     
    readme=read_me(new_directory,csv_name,llmfeedback)

    
    

# code execution block
if __name__=="__main__":
    main()