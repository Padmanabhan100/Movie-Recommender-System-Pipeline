from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.signin, name='signin'),
    path('signin/', views.signin, name='signin_wurl'),
    path("post_signin/", views.post_signin, name='post_signin'),
    path('dashboard_panel/', views.dashboard_panel, name='dashboard_panel'),
    path('dashboard_panel/<str:movie_name>', views.dashboard_panel, name='dashboard_panel2'),
    path("upload_movie/", views.upload_movie, name='upload_movie'),
    path("post_upload/", views.post_upload, name='post_upload'),
    path('delete_movie/<str:movie_id>', views.delete_movie, name='delete_movie'),
   
]
