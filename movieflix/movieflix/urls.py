from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('dashboard/', include("dashboard.urls")),
    path('', include('movieflix_user.urls')),
    path('user/', include('movieflix_user.urls')),
    path('ml/', include('movieflix_ml.urls')),
]
