from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
def signup(request):
    return render(request, 'common/signup.html')

def signin(request):
    return render(request, 'common/signin.html')
