import os
import yaml
import json
import shutil
import logging

def read_params(path):
    # Open the file
    with open(path) as yaml_file:
        # Load the contents of file
        config = yaml.safe_load(yaml_file)

    # Return the file contentes
    return config


def create_dir(dirs:list):
    # Iterate through the list of directories
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)

def clean_dir(path:str):
    # If directory exists remove the contents of the folder
    if os.path.isdir(path):
        shutil.rmtree(path)


def save_local_df(df, path:str, header=False, name=None):
    if header:
        # Replace the spaces in column name to underscores
        new_cols = [col.replace(" ","_") for col in df.columns]

        if name == None:
            # Save the dataframe
            df.to_csv(path, index=False, header=new_cols)
        else:
            # Save the dataframe
            df.to_csv(os.path.join(path, name), index=False, header=new_cols)

    else:
        if name == None:
            # Save the dataframe
            df.to_csv(path, index=False)
        else:
            # Save the dataframe
            df.to_csv(os.path.join(path, name), index=False)
