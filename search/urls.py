from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_patents, name='search_patents'),
]

