from django.shortcuts import render, redirect
import pyrebase
from django.core.paginator import Paginator
import json
from fuzzywuzzy import fuzz
from django.conf import settings
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path
import pickle
from urllib.parse import unquote
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Google account configurations
config = {
  "apiKey": os.getenv("API_KEY"),
  "authDomain": os.getenv("AUTH_DOMAIN"),
  "projectId": os.getenv("PROJECT_ID"),
  "databaseURL": "https://movieflix-fb7c4-default-rtdb.asia-southeast1.firebasedatabase.app/",
  "storageBucket": "movieflix-fb7c4.appspot.com",
  "messagingSenderId": os.getenv("MESSAGE_SENDER_ID"),
  "appId": os.getenv("APP_ID"),
  "measurementId": os.getenv("MEASUREMENT_ID")
}

# Initializing the firabase sdk
firebase = pyrebase.initialize_app(config)

# Initializing the firebase storage service
storage = firebase.storage()


# Initialize the firebase database service
database = firebase.database()



@csrf_exempt
def signin(request):
    try:
        return render(request, 'dashboard/signin.html')
    except:
        return render(request, 'error/error.html')


@csrf_exempt
def post_signin(request):
    try:
        if request.method == 'POST':
            # Fetch email and password
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Check if user and password is an admin account
            # Reference to the "admin_accounts" child
            admin_accounts_ref = database.child("admin_accounts")

            # Check if the user exists in "admin_accounts"
            user_info = admin_accounts_ref.get()
            users = user_info.val()  # This will be a dictionary of user data
            print(users)

            # If user is an admin account
            if {"email":email, "password":password} in users:
                # Set session true
                request.session['admin_status'] = True
                # Go to panel
                return redirect('/dashboard/dashboard_panel')
            else:
                # Go to panel
                return redirect('/dashboard/signin')
                    
        else:
            # Take user to landing page
            return redirect('dashboad/signin')
    except:
        return render(request, 'error/error.html')

@csrf_exempt
def logout(request):
    try:
        request.session['admin_status'] = False
        return redirect('/dashboard/signin')
    except Exception as e:
        print(e)
        return redirect('/dashboard/signin')
    

@csrf_exempt
def dashboard_panel(request):
    try:
        # Fetch all movies from dashboard
        all_movies = database.child('movies').get().val()

        # Check if any name if given in GET request
        movie_name = request.GET.get('movie_name', False)

        if movie_name:
            filtered_movies = []
            for movie in all_movies:
                # Calculate similarity of titles
                sim_score = fuzz.ratio(movie['original_title'].lower(), movie_name.lower())

            # If Similarity greater than 90% then append
            if sim_score > 30: filtered_movies.append(movie)
                
            # Create a pajinator object
            paginator = Paginator(filtered_movies, 5)

            # Get the current page number
            page_number = request.GET.get('page',1)

            # Get the data for that page number
            page_data = paginator.get_page(page_number)

            return render(request, 'dashboard/dashboard.html', {"page_data": page_data})
        
        else:
            # Create a pajinator object
            paginator = Paginator(all_movies, 5)

            # Get the current page number
            page_number = request.GET.get('page',1)

            # Get the data for that page number
            page_data = paginator.get_page(page_number)

            return render(request, 'dashboard/dashboard.html', {"page_data": page_data})
    except:
        # Message error
        return render(request, 'error/error.html')

@csrf_exempt
def post_upload(request):
    try:
        if request.method == 'POST':
            title = request.POST.get('title')
            original_title = request.POST.get('original_title')
            overview = request.POST.get('overview')
            cast = request.POST.get('cast')
            genres = request.POST.get('genres')
            keywords = request.POST.get('keywords')
            id = request.POST.get('id')

            # Get the uploaded files
            movie_path = request.FILES['movie_path']
            poster_path = request.FILES['poster_path']
            

            # Upload the files to Firebase Storage
            movie_storage_path = movie_path.name
            poster_storage_path = poster_path.name

            storage.child(movie_storage_path).put(movie_path)
            storage.child(poster_storage_path).put(poster_path)

            # Get the download URLs for the uploaded files
            movie_url = storage.child(movie_storage_path).get_url(None)
            poster_url = storage.child(poster_storage_path).get_url(None)

            print(movie_url)
            print(poster_url)

            # Save movie details in Firebase Realtime Database
            movie_data = {
                "id": id,
                "title": title,
                "original_title": original_title,
                "overview": overview,
                "cast": cast,
                "genres": genres,
                "keywords": keywords,
                "movie_path": movie_url,
                "poster_url": poster_url
            }

            # Save movie data to the Firebase Realtime Database
            database.child("movies").child(id).set(movie_data)

            return HttpResponse("Movie uploaded successfully.")
        
    except Exception as e:
        # Message to show
        message = "Uploading movie failed, please check your internet connection or try again later!"

        # SHow page
        return render(request, 'error/error.html', {'message': e})
    

@csrf_exempt
def upload_movie(request):
    try:
        # Pass the upload movie page as True to hide navbar search
        upload_movie_page = True

        # Return page
        return render(request, 'dashboard/upload_movies.html', {'upload_movie_page': upload_movie_page})
    
    except:
        return render(request, 'error/error.html')

@csrf_exempt
def delete_movie(request, movie_id):
    try:
        # Use the movie_id to construct the path to the movie data
        movie_path = f"movies/{movie_id}"

        # Get the movie data from the Realtime Database
        movie_data = database.child(movie_path).get().val()

        if movie_data:
            # Delete the movie's poster and video files from Firebase Storage
            poster_url = movie_data.get("poster_url")
            movie_url = movie_data.get("movie_path")

            movie_url = movie_url.split("/")[-1].split("?")[0]
            poster_url = poster_url.split("/")[-1].split("?")[0]

             # Process url to store the url in its original format
            movie_url = unquote(movie_url)
            poster_url = unquote(poster_url)

            if poster_url:
                poster_name = os.path.basename(poster_url).split("&")[0]
                storage.delete(name=poster_name, token=None)
                
            #if movie_url:
                movie_name = os.path.basename(movie_url).split("&")[0]
                storage.delete(name=movie_name, token=None)

            # Delete the movie data from the Realtime Database
            database.child(movie_path).remove()

            return HttpResponse("Movie and associated files deleted successfully.")

        else:
            # Show movie not found error
            message = "Movie not found!"

            # Return page
            return render(request, "error/error.html", {"message": message})
        
    except Exception as e:
        print(e)
        return render(request, "error/error.html", {"message": e})
       