import os
import argparse
import pandas as pd
from src.utils.common_utils import read_params, save_local_df, create_dir

def clean_data(path):
    # Load the configuration file
    config = read_params(path)

    # Load the path where the raw data is stored
    raw_local_data_dir = config['artifacts']['raw_local_data_dir']

    # Get the list of names of the datasets to load
    dataset_name = config['artifacts']['dataset_name']

    
    # Get the absolute path of the dataset
    dataset_abs_path = f"{raw_local_data_dir}\{dataset_name}"

    # Load the dataset into dataframe
    ratings = pd.read_csv(dataset_abs_path) 


    # Fetch the location of the file to save this clean data
    clean_local_data_dir = config['artifacts']['clean_local_data_dir']
    
    # Save the clean dataset
    create_dir([clean_local_data_dir])

    # Save the dataframe
    save_local_df(ratings, clean_local_data_dir, True, 'clean_data.csv')

def main(path='params.yaml'):
    try:
        # Fetch the data according to the arguments passed
        clean_data(path = path)
    
    except Exception as e:
        raise e

if __name__ == '__main__':
    # Initialize an argument parser object
    args = argparse.ArgumentParser()

    # Adding arguments to our created object
    args.add_argument("--config", default='params.yaml')

    # Fetch the arguments passed by user
    parsed_args = args.parse_args()

    # Fetch the data from the path mentioned in the config file(params.yaml)
    try:
        # Fetch the data according to the arguments passed
        clean_data(path = parsed_args.config)
    
    except Exception as e:
        raise e