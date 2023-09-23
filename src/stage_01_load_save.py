import pandas as pd
import argparse
from src.utils.common_utils import read_params, create_dir, save_local_df


# A function which will fetch the data from the mentioned source(params.yaml)
def get_data(path):
    # Read the config file using our utility
    config = read_params(path)

    # Fecthing the raw data path from the param.yaml
    raw_data_path1 = config['data_source']['ratings']
    raw_data_path2 = config['data_source']['movies_metadata']

    # Fetch the path of the raw_local_data_dir and artifacts_dir
    raw_local_data_dir = config['artifacts']['raw_local_data_dir']
    artifacts_dir = config['artifacts']['artifacts_dir']


    # Create the above raw_local_data_dir and artifacts dir to dump data
    create_dir([artifacts_dir, raw_local_data_dir])

    # Read the data from the remote source 
    ratings = pd.read_csv(raw_data_path1)
    movies_md = pd.read_csv(raw_data_path2, low_memory=False)

    # Save the loaded data into the raw_local_data_dir
    save_local_df(ratings, raw_local_data_dir, header=True, name='ratings.csv')
    save_local_df(movies_md, raw_local_data_dir, header=True, name='movies_md.csv')

def main(path='params.yaml'):
    try:
        # Fetch the data according to the arguments passed
        get_data(path = path)
    
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
        get_data(path = parsed_args.config)
    
    except Exception as e:
        raise e