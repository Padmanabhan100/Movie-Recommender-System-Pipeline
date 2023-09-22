from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('movieflixapp.urls')),
    path('user/', include('movieflix_user.urls')),
    path('creator/', include('movieflix_creator.urls')),
]
