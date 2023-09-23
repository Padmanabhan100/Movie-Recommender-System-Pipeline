from django.shortcuts import render
from src import Training

# Create your views here.
def train_model(request):
    # Train the model
    Training.main()

    # Return the dashboard
    return render(request, 'ml/index.html')