from . import views
from django.urls import path, re_path


urlpatterns = [
    path("", views.signup, name='signup_page'),
    path("signup/", views.signup, name='signup_page'),
    path("signin/", views.signin, name='signin_page'),
    path("post_signup/", views.post_signup, name='post_signup_page'),
    path("post_signin/", views.post_signin, name='post_signin_page'),
    path("logout/", views.logout, name='logout_session'),
    path("landing/", views.landing, name='landing_page'),
    path("search/", views.search, name='search_movies'),
    path("payment/", views.payment, name='payment'),
    path('post_payment/', views.post_payment, name='post_payment'),
    path('movie_player/', views.video_player, name='video_player'),
    path('renew/', views.renew, name='renew'),
    path('post_renew/', views.post_renew, name='post_renew'),
    path('renew_payment/', views.renew_payment, name='renew_payment'), # Load payment page(with razorpay button)
    path('renew_payment_done/', views.renew_payment_done, name='renew_payment_done'),
]
