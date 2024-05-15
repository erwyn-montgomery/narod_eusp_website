from django.contrib import admin
from django.urls import path, include
from search.views import SearchResults, AdvancedSearchView, AdvancedSearchResultsView


urlpatterns = [
    path("results/", SearchResults.as_view(), name="search_results"),
    path("advanced_search/", AdvancedSearchView.as_view(), name="advanced_search"),
    path("advanced_search/results", AdvancedSearchResultsView.as_view(), name="advanced_search_results"),
]
