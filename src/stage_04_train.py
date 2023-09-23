import os
import argparse
import pandas as pd
import pickle
import time
from surprise import Dataset, Reader
from surprise.prediction_algorithms.knns import KNNBasic
from surprise.prediction_algorithms.matrix_factorization import SVD
from src.utils.common_utils import read_params, create_dir, clean_dir



def train_model(path, model, model_type):
    # Load the config file
    config = read_params(path)

    # Get the path of folder to save latest model
    latest_model_dir = config['artifacts']['latest_model_dir']

    # Check if latest model dir exist, if it does delete it
    clean_dir(latest_model_dir)

    # Create a latest model dir to save new model
    create_dir([latest_model_dir])
    
    # Fetch the path of train data dir
    train_data_dir = config['artifacts']['train_data_dir']

    # Create the path of the training file
    train_path = os.path.join(train_data_dir,'train.csv')

    # Load the train dataset
    df = pd.read_csv(train_path)

    # Initialize a surprise reader object
    reader = Reader(line_format='user item rating', sep=',', rating_scale=(0,5), skip_lines=1)

    # Load the data
    data = Dataset.load_from_df(df[['userId','movieId','rating']], reader=reader)

    # Build trainset object(perform this only when you are using whole dataset to train)
    trainset = data.build_full_trainset()

    # Do training based on conditions
    if model == "model_based":
        # Initialize model
        svd = SVD()

        # Train the model
        svd.fit(trainset)

        # Save the model in the latest model directory
        model_path = os.path.join(latest_model_dir,'model.sav')
        pickle.dump(svd, open(model_path, 'wb'))

        # Save a copy inside the django app to access the latest model
        model_path = os.path.join("movieflix", "manual_artifacts" , 'model.sav')
        pickle.dump(svd, open(model_path, 'wb'))


    elif model == "memory_based":
        if model_type == 'user_user_based':
            #Declaring the similarity options.
            sim_options = {'name': 'cosine',
                        'user_based': True}

            # KNN algorithm is used to find similar items
            sim_user = KNNBasic(sim_options=sim_options, verbose=False, random_state=33)

            # Train the algorithm on the trainset, and predict ratings for the testset
            sim_user.fit(trainset)


            # Save the model in the latest model directory
            model_path = os.path.join(latest_model_dir,'model.sav')
            pickle.dump(sim_user, open(model_path, 'wb'))

            # Save a copy inside the django app to access the latest model
            model_path = os.path.join("movieflix", "manual_artifacts" , 'model.sav')
            pickle.dump(sim_user, open(model_path, 'wb'))

        
        elif model_type == 'item_item_based':
            #Declaring the similarity options.
            sim_options = {'name': 'cosine',
                        'user_based': False}

            # KNN algorithm is used to find similar items
            sim_item = KNNBasic(sim_options=sim_options, verbose=False, random_state=33)

            print("Train Started")
            # Train the algorithm on the trainset, and predict ratings for the testset
            sim_item.fit(trainset)
            print("Train end")


            # Save the model in the latest model directory
            model_path = os.path.join(latest_model_dir,'model.sav')
            pickle.dump(sim_item, open(model_path, 'wb'))

            # Save a copy inside the django app to access the latest model
            model_path = os.path.join("movieflix", "manual_artifacts" , 'model.sav')
            pickle.dump(sim_item, open(model_path, 'wb'))


        else:
            print("Select a model type")
        
    else:
        print("Select a model!")


def main(path="params.yaml", model='model_based', model_type=''):
    try:
        # Fetch the data according to the arguments passed
       train_model(path = path, model=model, model_type=model_type)
    
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
        train_model(path = parsed_args.config, model=parsed_args.model, model_type=parsed_args.model_type)
    
    except Exception as e:
        raise e