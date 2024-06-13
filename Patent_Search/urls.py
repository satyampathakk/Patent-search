from django.contrib import admin
from django.urls import include, path
import search

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('search.urls')),
    
]