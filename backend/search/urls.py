from django.urls import path

from .views import (
    FilterOptionsView,
    HybridSearchView,
    SemanticSearchView,
    StructuredSearchView,
)

urlpatterns = [
    path("search/semantic/", SemanticSearchView.as_view()),
    path("search/structured/", StructuredSearchView.as_view()),
    path("search/hybrid/", HybridSearchView.as_view()),
    path("filters/", FilterOptionsView.as_view()),
]
