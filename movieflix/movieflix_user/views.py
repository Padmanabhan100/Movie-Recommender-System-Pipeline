from django.shortcuts import render, redirect
import pyrebase
from django.core.paginator import Paginator
from fuzzywuzzy import fuzz
import json
import razorpay
import datetime
from django.conf import settings
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path
import pickle
from django.views.decorators.csrf import csrf_exempt
import traceback


# Load the .env file
load_dotenv()

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


# Google account configurations
config = {
  "apiKey": os.getenv("API_KEY"),
  "authDomain": os.getenv("AUTH_DOMAIN"),
  "projectId": os.getenv("PROJECT_ID"),
  "databaseURL": os.getenv("DATABASE_URL"),
  "storageBucket": os.getenv("STORAGE_BUCKET"),
  "messagingSenderId": os.getenv("MESSAGE_SENDER_ID"),
  "appId": os.getenv("APP_ID"),
  "measurementId": os.getenv("MEASUREMENT_ID")
}

# Initializing the firabase sdk
firebase = pyrebase.initialize_app(config)

# Initializing the firebase authentication service
auth = firebase.auth()

# Initialize the firebase database service
database = firebase.database()

# Create your views here.
@csrf_exempt
def signup(request):
    return render(request, 'user/signup.html')

@csrf_exempt
def post_signup(request):
    # Check if the request is a post request
    if request.method == 'POST':
        # Fetch the email and password form the POST request
        email = request.POST.get('email')
        password = request.POST.get('password')
        plan = request.POST.get('plan')

        # Fetch the months and amount of subscription
        amount = int(plan.split(":")[0])
        months = int(plan.split(":")[-1])

        # Crete an order context
        order_context = {
            "amount": amount*100,
            "email":email,
            'password':password,
            'months':months,
            "currency": "INR",
            "payment_capture": '1'
        }

        # Set payment data to session
        request.session['payment_data'] = order_context

        # Redirect to the sign in page
        return redirect("/user/payment")
    
    
def load_content(landing=False, search=False, movie_query='', personalized_recommendations=[], similar_recommendation=[]):
    # Check if all_movies.json file exists in the system
    if os.path.exists("all_movies.json"):

        # Get the file's metadata
        file_md = os.stat("all_movies.json")

        # Get the time when file was dwnloaded
        file_time = file_md.st_mtime

        # Get the time difference from current datetime
        time_difference = datetime.datetime.now().timestamp() - file_time

        # If it exceeds 24 hours delete it
        if time_difference >= 86400:
            # Delete that file
            os.remove("all_movies.json")

            # Load all the movies from the database
            movies = database.child("movie").get().val()
                
            # Dump the movies fetched in a varaible
            movies_json = json.dumps(movies, indent=4)

            # Write the movies fetched in a file   
            with open("all_movies.json", "w") as file:
                file.write(movies_json)  
    else:
        # Load all the movies from the database
        movies = database.child("movie").get().val()
                
        # Dump the movies fetched in a varaible
        movies_json = json.dumps(movies, indent=4)

        # Write the movies fetched in a file   
        with open("all_movies.json", "w") as file:
            file.write(movies_json)


    # Open the movies file and read all the data
    with open("all_movies.json", "r") as file:
            # Load all movies from the file
            movies = json.load(file)
               
    if landing:
        # Empty list to store movies
        action_movies = []
        comedy_movies = []
        romance_movies = []
        animation_movies = []

        # Iterate through all movies to fetch movies of mentioned genres
        for movie in movies:
            # Split the genre string of the iterated movie
            all_genres = movie.get("genres", "").split()

            # Check for genre matching and size to display on screen
            if "Action" in all_genres and len(action_movies)<20:
                action_movies.append(movie)
            
            if "Comedy" in all_genres and len(comedy_movies)<20:
                comedy_movies.append(movie)

            if "Romance" in all_genres and len(romance_movies)<20:
                romance_movies.append(movie)

            if "Animation" in all_genres and len(animation_movies)<20:
                animation_movies.append(movie)

            if len(action_movies) == 20 and len(comedy_movies) == 20 and len(romance_movies) == 20 and len(animation_movies) == 20:
                break
        

        movies_by_genre = {
            "action": action_movies,
            "comedy": comedy_movies,
            "romance": romance_movies,
            "animation":animation_movies
        }

        return movies_by_genre
    
    elif personalized_recommendations:
        # Get all the recommendations movie data
        recommended_movies = [movie for movie in movies if movie['id'] in personalized_recommendations]

        # Return the list of recommendations
        return recommended_movies
    
    elif similar_recommendation:
       # Convert movie id to int
        movie_id = int(similar_recommendation[0])

        # Get the distances of all movies for the given movie
        global similarity, movie_sim_map

        # Get the id of the movie in similarity matrix
        movie_id = movie_sim_map[movie_sim_map['id'] == movie_id].index[0]

        # Get the distances of all the movies for the given movie id
        distances = similarity[movie_id]

        # Sort the distances in descending and get the first N recommendations
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:10]

        # Create a list of movie ids
        recommendations = []

        # Append the id of the movie to the list
        for idx in movie_list:
            # Convert similarity ids to movie ids
            idx = movie_sim_map.iloc[idx[0]]

            # Fetch the movie of the recommended id from the database
            record = database.child('movie').child(f"{idx[0]}").get().val()

            # Add it to recommendations list
            recommendations.append(record)

        # Return the list of recommendations
        return recommendations

    elif search:
        # Empty list to store movies
        movies_list = []

        # Iterate through all the movies and get the names
        for movie in movies:
            # Get the name of the movie
            movie_title = movie.get("original_title")

            # Get the similarity scores between strings
            sim_score = fuzz.ratio(movie_title.lower(), movie_query.lower())

            # Check if score greter than 0.7 and append to list
            if sim_score >= 0.99:
                movie_and_score = {'movie':movie, 'score':sim_score}
                movies_list.append(movie_and_score)

        # Sort the movies based on similarity scores in descending order
        movies_list = sorted(movies_list, key=lambda x:x['score'], reverse=True)

        return movies_list

@csrf_exempt
def signin(request):
    return render(request, 'user/signin.html')


# Function to check subscription status
def is_subscription_over(user_id):
    try:
        # Retrieve user data from Firebase
        user_data = database.child("users").child(user_id).get().val()

        # Check if user_data is not None
        if user_data:
            # Extract relevant data
            user_date_str = user_data.get("date", "")
            user_months = user_data.get("months", 0)

            # Parse the date string into a datetime object
            user_date = datetime.datetime.strptime(user_date_str, "%Y-%m-%d").date()

            # Calculate the current date
            current_date = datetime.date.today()

            # Calculate the subscription end date by adding months to the user's date
            subscription_end_date = user_date + datetime.timedelta(days=30 * user_months)

            # Check if the current date is greater than the subscription end date
            if current_date > subscription_end_date:
                return True  # Subscription is over
            else:
                return False  # Subscription is still active
        else:
            return False  # User data not found

    except Exception as e:
        print("Error:", str(e))
        return False  # Handle any exceptions
    

@csrf_exempt
def post_signin(request):
    if request.method == 'POST':
        # Fetch email and password
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try authentiating the user
        try:
            # Signin the user if it exists
            user = auth.sign_in_with_email_and_password(email, password)
        except:
            return redirect('/user/signin')
        
        
        # Fetch the user_id from the created user object
        user_id = user['localId']

        # Set the localid in request sessions
        request.session['localId'] = user_id

        print("is subscription over?", is_subscription_over(user_id))

        # Check if subscription is over
        if not is_subscription_over(user_id):
            # Fetch the session_id of user
            session_id = user['idToken']

            # Set the session_id in the requests
            request.session['uid'] = str(session_id)


            # Show the landing page if subscription is not finished
            return redirect('/user/landing')
    else:
        # Take user to landing page
        return redirect('/user/signin')
    
def landing(request):
    try:
        # Load the content only if user session id exists(has not logged out)
        if request.session['uid']:

            # Load the content
            movies_by_genre = load_content(landing=True)

            # Get the manual artifacts dir
            manual_artifacts_dir = Path(__file__).resolve().parent.parent / 'manual_artifacts'

            # Get the artifacts directory
            artifacts_dir = Path(__file__).resolve().parent.parent / 'artifacts'

            # Load the similarity matrix and set as global variable
            global similarity
            similarity = np.load(f"{manual_artifacts_dir}/similarity.npy")

            # Load the movie_id and similarity mappings
            global movie_sim_map 
            movie_sim_map = pd.read_csv(f"{manual_artifacts_dir}/movie_similarity_id_mapping.csv")
            print("read movie_sim_map --> ",movie_sim_map.head())


            # Get user id to get personalized recommendations for the user
            user_id = request.session['localId']

            # Recommend movies ids
            recommendations = get_personalized_recommendation(artifacts_dir=artifacts_dir, user_id=3)

            # Fetch the recommended movies from db
            recommendations = load_content(personalized_recommendations=recommendations)
                
            # Show the landing page
            return render(request, 'user/index.html', {"movies_by_genre":movies_by_genre, 'recommendations':recommendations})
        
        else:
            return redirect('/user/signin')
        
    except Exception as e:
        traceback.print_exc()
        print("Exception from landing:", e)
        return render(request, 'user/signin.html')

@csrf_exempt
def logout(request):
    try:
        del request.session['uid']
        del request.session['localId']
        return redirect('/user/signup')
    except Exception as e:
        print(e)
        return redirect('/user/signin')
    
def search(request):
    try:
        # Check if user session exists
        request.session['localId']

        if request.method == 'GET':
            # Get the movie name 
            movie_name = request.GET.get('searched_movie_title')
            print("Movie name --", movie_name)


            # Find the matching movies
            movie_list = load_content(search=True, movie_query=movie_name)

            # Create a paginator
            paginator = Paginator(movie_list, 5)  # 5 items per page

            # Get the total number of pages
            num_pages = paginator.num_pages

            # As it is a post request
            page_number = request.GET.get('page',1)
            
            # Get the data of that page
            page_obj = paginator.get_page(page_number)

            print(page_obj)
            # Show the search page
            return render(request, 'user/search_landing.html', {"page_obj":page_obj, 'searched_movie_title':movie_name, "num_pages":num_pages})

        elif request.method == 'GET':
            # Get the page number
            page_number = request.GET.get('page')

            # Find the matching movies
            movie_list = load_content(search=True, movie_query=movie_name)
            
            # Creata a paginator
            paginator = Paginator(movie_list, 5)  # 5 items per page

            # Get the data of that page
            page_obj = paginator.get_page(page_number)

            # Show the search page
            return render(request, 'user/search_landing.html', {"page_obj":page_obj})
    
    except:
        # If user session doesnt exist it will raise exception
        return render(request,'user/signin.html')

def payment(request):
    try:
        # Get the amount from the request session
        payment_data = request.session['payment_data']

        # Show the payment page
        return render(request, 'user/payment.html', {'payment_data': payment_data})

    except:
        return render(request, 'user/signin.html')

@csrf_exempt
def post_payment(request):
    # Get email and password from the session
    email = request.session['payment_data']['email']
    password = request.session['payment_data']['password']
    months = request.session['payment_data']['months']

    # Delete the payment session
    del request.session['payment_data']

    # Create a new user object
    user = auth.create_user_with_email_and_password(email, password)

    # Fetch the user_id from the created user object
    user_id = user['localId']

    # Creating a dictionary to push the data to the firebase database
    data = {"email": email, 'password': password, "months":months, 'date':str(datetime.datetime.now().date())}

    # Store to database
    database.child("users").child(user_id).set(data)

    # Redirect to signin page
    return redirect('/user/signin')


def get_personalized_recommendation(artifacts_dir=None, user_id=None, top_n=5):
    # Load the model
    model_path = os.path.join(artifacts_dir,"latest_model_dir", 'model.sav')

    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)

   
   # Read the ratings data and movie meta data as dataframe
    ratings_path = os.path.join(artifacts_dir,"raw_local_data_dir", "ratings.csv")
    movie_md_data_path = os.path.join(artifacts_dir, "raw_local_data_dir", "movies_md.csv")
    ratings = pd.read_csv(ratings_path)
    movie_md = pd.read_csv(movie_md_data_path,low_memory=False)

    # Select ratings data and metadata with vote count > 55
    movie_md = movie_md[movie_md['vote_count']>55][['id','title']]

    # IDs of movies with count more than 55
    movie_ids = [int(x) for x in movie_md['id'].values]

    # Select ratings of movies with more than 55 counts
    ratings = ratings[ratings['movieId'].isin(movie_ids)]

    # Reset Index
    ratings.reset_index(inplace=True, drop=True)
    
    # Inititlize a reader object
    #reader = Reader(line_format="user item rating", sep=',', rating_scale=(1, 5), skip_lines=1)
    
    # Inititlize a dataset object form dataframe
    #data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader=reader)
    
    # creating an empty list to store the recommended product ids
    recommendations = []
    
    # creating an user item interactions matrix 
    user_movie_interactions_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')
    
    # extracting those product ids which the user_id has not interacted yet
    non_interacted_movies = user_movie_interactions_matrix.loc[user_id][user_movie_interactions_matrix.loc[user_id].isnull()].index.tolist()
    
    # looping through each of the product ids which user_id has not interacted yet
    for item_id in non_interacted_movies:
        
        # predicting the ratings for those non interacted product ids by this user
        est = model.predict(user_id, item_id).est
        
        # appending the predicted ratings
        movie_id = movie_md[movie_md['id']==str(item_id)]['id'].values[0]
        recommendations.append((movie_id, est))

    # sorting the predicted ratings in descending order
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # Convert to pure list with only recommendation id
    recommendations = [int(item[0]) for item in recommendations]

    # Print the recommendations
    return recommendations[:top_n]
    

def get_recommendations(movie_id):
    # Convert movie id to int
    movie_id = int(movie_id)

    # Get the distances of all movies for the given movie
    global similarity, movie_sim_map

    # Get the if of the movie in similarity matrix
    movie_id = movie_sim_map[movie_sim_map['id'] == movie_id].index[0]

    # Get the distances of all the movies for the given movie id
    distances = similarity[movie_id]

    # Sort the distances in descending and get the first N recommendations
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:10]

    # Create a list of movie ids
    recommendations = []

    # Append the id of the movie to the list
    for idx in movie_list:
        # Convert similarity ids to movie ids
        idx = movie_sim_map.iloc[idx[0]]

        # Fetch the movie of the recommended id from the database
        record = database.child('movie').child(f"{idx[0]}").get().val()

        # Add it to recommendations list
        recommendations.append(record)

    # Return the list of recommendations
    return recommendations
    
def video_player(request):
    # Get the movie data
    movie_id = str(request.GET.get('id'))
    movie_title = request.GET.get('title')
    movie_cast = request.GET.get('cast')
    movie_path = request.GET.get('movie_path')
    movie_rating = request.GET.get('rating')

    # Get user id stored in session variables
    user_id = request.session['localId']

    # Get the recommendations
    recommendations = load_content(similar_recommendation=[movie_id])

    # Create a movie data dictionary
    movie_data = {'id':movie_id ,'title': movie_title, 'cast': movie_cast, 'movie_path': movie_path}


    # If rating has been given
    if movie_rating:
        # Get the location to add it
        user_ratings_ref = f'users/{user_id}/ratings'

        # Get all the user ratings
        user_ratings = database.child(user_ratings_ref).get().val() or {}

        # Update the user's ratings with the new rating
        user_ratings[movie_id] = int(movie_rating)

        # Set the updated ratings object in Firebase
        database.child(user_ratings_ref).set(user_ratings)
            
    return render(request, 'user/video_player.html', {'movie_data': movie_data, "recommendations":recommendations})

def renew(request):
    try:
        # Get the session id of the user
        request.session['localId']

        # Return the renew page
        return render(request, 'user/renew.html')
    except:
        # If session doesn't exist, it will raise an exception
        return render(request, 'user/signin.html')

      


"""
GETS THE PLAN FROM THE RENEW PAGE AND REDIRECTS
TO THE URL RENEW_PAYMENT TO LOAD THE PAYMENT PAGE
WHICH HAS THE RAZORPAY BUTTON
"""

def post_renew(request):
    # Check if the request is a post request
    if request.method == 'POST':
        # Fetch the email and password form the POST request
        plan = request.POST.get('plan')

        # Fetch the months and amount of subscription
        amount = int(plan.split(":")[0])
        months = int(plan.split(":")[-1])

        # Crete an order context
        order_context = {
            "amount": amount*100,
            'months':months,
            "currency": "INR",
            "payment_capture": '1'
        }

        # Set payment data to session
        request.session['payment_data'] = order_context

        # Redirect to the sign in page
        return redirect("/user/renew_payment")
    
"""
LOADS PAYMENT DATA FROM THE SESSION AND RENDERS
THE PAYMENT PAGE WITH RAZORPAY BUTTON
"""
def renew_payment(request):
    # Get the amount from the request session
    payment_data = request.session['payment_data']

    # Show the payment page
    return render(request, 'user/payment.html', {'payment_data': payment_data})
    
"""
ONCE THE PAYMENT IS SUCCESSFUL, UPDATES THE SUBSCRIPTION MONTHS
OF THE USER(USER ID) FETCHED FROM THE SESSION VARIABLE SET WHILE
LOGIN.
"""

def renew_payment_done(request):
    # Get the months and update the subscription
    months = request.session['payment_data']['months']

    # Delete the payment session
    del request.session['payment_data']

    # Get the user's id from the session varaible
    user_id = request.session['localId']

    # Update the data in db
    database.child("users").child(user_id).update({"months":months})

    # Return to landing page
    return redirect('/user/landing')

