from django.urls import path

from .views import (
    FileConfigView,
    HealthView,
    ResumeByEmailView,
    ResumeCollectionView,
    ResumeDetailView,
)

API_V1_PREFIX = "api/v1/"

urlpatterns = [
    path(f"{API_V1_PREFIX}resumes/", ResumeCollectionView.as_view()),
    path(f"{API_V1_PREFIX}resumes/<str:uid>/", ResumeDetailView.as_view()),
    path(f"{API_V1_PREFIX}resumes/by-email/<str:email>/", ResumeByEmailView.as_view()),
    path(f"{API_V1_PREFIX}health/", HealthView.as_view()),
    path(f"{API_V1_PREFIX}config/file-types/", FileConfigView.as_view()),
]
