from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movieflix_user.urls')),
    path('user/', include('movieflix_user.urls')),
]
