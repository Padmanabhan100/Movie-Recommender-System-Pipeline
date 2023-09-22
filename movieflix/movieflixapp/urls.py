from . import views
from django.urls import path


urlpatterns = [
    path("/", views.signup, name='signup_page'),
    path("signup/", views.signup, name='signup_page'),
    path("signin/", views.signin, name='signin_page'),
]
