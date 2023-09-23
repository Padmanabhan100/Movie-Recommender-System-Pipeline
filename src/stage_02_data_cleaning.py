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
    datasets = config['artifacts']['datasets']

    # Load the data as dataframes for processing
    dataframes = []

    for dataset in datasets:
        # Get the absolute path of the dataset
        dataset_abs_path = f"{raw_local_data_dir}\{dataset}"

        if dataset == 'movies_md.csv':
            # Load the dataset into dataframe
            df = pd.read_csv(dataset_abs_path, low_memory=False) 
        else:
            # Load the dataset into dataframe
            df = pd.read_csv(dataset_abs_path) 

        # Append to dataframes list
        dataframes.append(df)

    # Separate the dataframes
    ratings, movie_md = dataframes

    # Cleaning the dataset
    # movie dataframe with votes more than 55
    movie_md = movie_md[movie_md['vote_count']>55][['id','title']]

    # IDs of movies with count more than 55
    movie_ids = [int(x) for x in movie_md['id'].values]

    # Select ratings of movies with more than 55 counts
    ratings = ratings[ratings['movieId'].isin(movie_ids)]

    # Reset Index
    ratings.reset_index(inplace=True, drop=True)

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