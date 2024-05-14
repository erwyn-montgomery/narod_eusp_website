from django.contrib import admin
from django.urls import path, include
from search import views


urlpatterns = [
    path("results/", views.SearchResults.as_view(), name="search_results")
]
