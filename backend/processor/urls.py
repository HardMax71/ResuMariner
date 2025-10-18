from django.urls import path

from .views import (
    FileConfigView,
    HealthView,
    ResumeByEmailView,
    ResumeCollectionView,
    ResumeDetailView,
)

urlpatterns = [
    path("resumes/", ResumeCollectionView.as_view()),
    path("resumes/<str:uid>/", ResumeDetailView.as_view()),
    path("resumes/by-email/<str:email>/", ResumeByEmailView.as_view()),
    path("health/", HealthView.as_view()),
    path("config/file-types/", FileConfigView.as_view()),
]
