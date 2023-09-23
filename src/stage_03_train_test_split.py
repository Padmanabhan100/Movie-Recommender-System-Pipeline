import os
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from src.utils.common_utils import read_params, create_dir, clean_dir, save_local_df

def split_data(path, model, model_type):
    # Load the config file
    config = read_params(path)

    # Read the train directory path and test dir path
    train_data_dir = config['artifacts']['train_data_dir']
    test_data_dir = config['artifacts']['test_data_dir']

    # Create the train data directory and test data directory
    create_dir([train_data_dir, test_data_dir])

    # Get the path of the clean dataset
    clean_local_data_dir = config['artifacts']['clean_local_data_dir']

    # Create the abs path of file
    clean_data_abs_path = os.path.join(clean_local_data_dir,'clean_data.csv')

    # Load the daatframe
    ratings = pd.read_csv(clean_data_abs_path)

    # Select the train and test ratio form params based on model name
    if model == "model_based":
        train_size = config['model']['model_based']['train_size']
        random_state = config['model']['model_based']['random_state']
    
    elif model == "memory_based":
        if model_type == "item_item_based":
            train_size = config['model']['memory_based']['item_item_based']['train_size']
            random_state = config['model']['memory_based']['item_item_based']['random_state']

        elif model_type == "user_user_based":
            train_size = config['model']['memory_based']['user_user_based']['train_size']
            random_state = config['model']['memory_based']['user_user_based']['random_state']


    # Split the dataset into trainset and test set
    train_data, test_data = train_test_split(ratings, train_size=train_size, random_state=random_state)

    # Convert array to dataframe
    train_data = pd.DataFrame(train_data)
    test_data = pd.DataFrame(test_data)


    # Save the train and test dataset
    save_local_df(train_data, train_data_dir, True, name='train.csv')
    save_local_df(test_data, test_data_dir, True, name='test.csv')


def main(path='params.yaml', model='model_based', model_type=''):
    try:
        # Fetch the data according to the arguments passed
        split_data(path =path ,model=model, model_type=model_type)
    
    except Exception as e:
        raise e

if __name__ == '__main__':
    # Initialize an argument parser object
    args = argparse.ArgumentParser()

    # Adding arguments to our created object
    args.add_argument("--config", default='params.yaml')
    args.add_argument("--model", default='model_based')
    args.add_argument("--model_type", default='')


    # Fetch the arguments passed by user
    parsed_args = args.parse_args()

    # Fetch the data from the path mentioned in the config file(params.yaml)
    try:
        # Fetch the data according to the arguments passed
        split_data(path = parsed_args.config ,model=parsed_args.model, model_type=parsed_args.model_type)
    
    except Exception as e:
        raise e