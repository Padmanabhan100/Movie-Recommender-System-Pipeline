from src import stage_01_load_save, stage_02_data_cleaning, stage_03_train_test_split, stage_04_train, stage_05_evaluate


def main():
    try:
        # Run Stage - 1
        print("RUNNING STAGE-1: DATA INGESTION STAGE")
        stage_01_load_save.main()

        # Run Stage - 2
        print("RUNNING STAGE-2: DATA CLEANING STAGE")
        stage_02_data_cleaning.main()

        # Run Stage - 3
        print("RUNNING STAGE-3: TRAIN TEST SPLIT STAGE")
        stage_03_train_test_split.main()

        # Run Stage - 4
        print("RUNNING STAGE-4: MODEL TRAINING STAGE")
        stage_04_train.main()

        # Run Stage - 5
        print("RUNNING STAGE-5: MODEL EVALUATION STAGE")
        stage_05_evaluate.main()

    except Exception as e:
        print(f"Error In Training Pipeline: {e}")