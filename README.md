# Movie-Recommender-System-Pipeline

## Table of Contents
1. [Introduction](#introduction)
2. [Technologies](#technologies)
3. [MLOps Architecture](#mlops-architecture)
4. [Project Structure](#project-structure)
5. [License](#License)

## Introduction
This repository contains the implementation of a movie recommendation system as part of an MLOps project. The system includes two types of recommender models: memory-based and model-based. The MLOps architecture includes pipelines for the model-based model, allowing for easy switching between user-user based or item-item based models with a single argument.

## Technologies
The project uses several technologies to implement the MLOps architecture:

- **Django**: The main framework used for building the web application.
  
- **DVC**: Used for pipeline orchestration and experiment tracking.
  
- **Google Storage Bucket**: Used for storing the similarity matrix required for the memory-based model.
  
- **Google Artifacts Registry**: Used for storing the containerized pipeline.

- **Google Cloud Run**: Used for deploying the docker image.

![Untitled design](https://github.com/Padmanabhan100/Movie-Recommender-System-Pipeline/assets/73405735/8efa82b5-cdb2-4036-91fa-ff3c0fee0077)


## MLOps Architecture
The project follows a Level-1 MLOps architecture, which includes the following steps:

<img src="https://cloud.google.com/static/architecture/images/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning-3-ml-automation-ct.svg">

1. **Data Versioning**: Versioning the datasets used in the ML pipeline to ensure reproducibility of experiments.
2. **Model Training**: Training the ML model using the versioned data. The training process is typically automated and can be triggered based on various events such as changes in the data or code.
3. **Model Versioning**: After training, the model is versioned. This allows for easy rollback to previous versions if needed.
4. **Model Deployment**: The versioned model is then deployed to a production environment. This could be a server, a cloud-based platform, or even an edge device.
5. **Monitoring**: Once the model is deployed, it's important to monitor its performance to ensure it's making accurate predictions. If the model's performance degrades, it may need to be retrained with new data.
6. **Automation**: The entire pipeline from data versioning to model deployment and monitoring is automated, allowing for continuous integration and delivery of ML models.

## Project Structure
The main directory of the project is the `movieflix` directory, which is a Django project. The project structure is as follows:

```
movieflix
│
├── artifacts
├── movieflix.ml
├── movieflix_user
├── templates
├── static
├── db.sqlite3
└── manage.py
```

Each of these directories and files serve a specific purpose in the Django application:

- `artifacts`: This directory contain data files, models, and other resources which are result of MLOPS pipeline and needed by your application.
- `movieflix.ml`: This is a Django app to implement continouos training by going to a route.
- `movieflix_user`: This is a Django app handling user-related functionality this is where the recommendation system is implemented.
- `templates`: This directory contains Django templates for your application.
- `static`: This directory contains static files like CSS, JavaScript, and images.
- `db.sqlite3`: This is the SQLite database file for your application(not required as we have integrated firebase).
- `manage.py`: This is a command-line utility that lets you interact with your Django project in various ways.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Thank you for your interest in the Movie Recommender System Pipeline! If you have any questions or need assistance, feel free to reach out.

Happy recommending! 🎬🍿