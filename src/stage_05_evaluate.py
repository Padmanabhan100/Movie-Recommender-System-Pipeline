import os
import pickle
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from surprise import Dataset, Reader, accuracy
from src.utils.common_utils import read_params, create_dir


def calculate_metrics(model, train_data, test_data):
    # Predictions for trainset and test set
    print("Predicting train")
    train_predictions = model.test(train_data)
    print("Predicting test")
    test_predictions = model.test(test_data)

    # Calculate metrics
    # For train
    train_rmse = accuracy.rmse(train_predictions)
    train_mse = accuracy.mse(train_predictions)
    train_mae = accuracy.mae(train_predictions)
    train_fcp = accuracy.fcp(train_predictions)

    # For test 
    test_rmse = accuracy.rmse(test_predictions)
    test_mse = accuracy.mse(test_predictions)
    test_mae = accuracy.mae(test_predictions)
    test_fcp = accuracy.fcp(test_predictions)

    # Create a dataframe of metrics
    metrics_dict = {"train_metrics":[train_rmse, train_mse, train_mae, train_fcp],
                    "test_metrics":[test_rmse, test_mse, test_mae, test_fcp]}
    
    # Also give the indexes
    metrics_df = pd.DataFrame(metrics_dict, index=['RMSE','MSE','MAE','FCP'])

    # Return metrics df
    return metrics_df


def evaluate_model(path):
    #  Load the configuration file
    config = read_params(path)

    # Fetch the train data path and test data path
    train_data_dir = config['artifacts']['train_data_dir']
    train_data_path = os.path.join(train_data_dir,'train.csv')

    test_data_dir = config['artifacts']['test_data_dir']
    test_data_path = os.path.join(test_data_dir,'test.csv')

    # Load the train data and test data
    train_data = pd.read_csv(train_data_path)
    test_data = pd.read_csv(test_data_path)

    # Convert the trainset and testset to Dataset object compatable with surprise module
    # Initialize a surprise reader object
    reader = Reader(line_format='user item rating', sep=',', rating_scale=(0,5), skip_lines=1)

    train_data = Dataset.load_from_df(train_data[['userId','movieId','rating']], reader=reader)
    test_data = Dataset.load_from_df(test_data[['userId','movieId','rating']], reader=reader)

    print("Building train set")
    train_data = train_data.build_full_trainset().build_testset()
    print("Building test set")
    test_data = test_data.build_full_trainset().build_testset()

    # Fetch the path of the latest model dir
    latest_model_dir = config['artifacts']['latest_model_dir']

    # Fetch the path of the model
    latest_model_path = f"{latest_model_dir}/{os.listdir(latest_model_dir)[0]}"

    print(latest_model_path)

    # Load the model
    model = pickle.load(open(latest_model_path, 'rb'))

    # Calculate the metrics
    metrics_df = calculate_metrics(model, train_data, test_data)

    # Load the path to store metrics
    metrics_dir = config['artifacts']['metrics_dir']

    # Create the directory
    create_dir([metrics_dir])

    # Create a bar plot for the metrics comparasion
    plot = metrics_df.plot(kind='bar', figsize=(10,10))

    # Set title and labels for the barplot
    plot.set_title("Recommender System Metrics Comparasion")
    plot.set_ylabel("Error")

    # Annotate the barplot
    for p in plot.patches:
        plot.annotate("{:.1f}".format(p.get_height()), (p.get_x(), p.get_height()))

    # Save the plot
    plt.savefig(f'{metrics_dir}/metrics.png')

    # Save the datframe
    metrics_df.to_csv(f"{metrics_dir}/metrics.csv", index=True, header=True)


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
        evaluate_model(path = parsed_args.config)
    
    except Exception as e:
        raise e