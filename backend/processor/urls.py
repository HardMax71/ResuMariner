from django.urls import path

from .views import CleanupJobsView, FileConfigView, HealthView, JobResultView, JobStatusView, UploadCVView

urlpatterns = [
    path("api/v1/upload/", UploadCVView.as_view()),
    path("api/v1/jobs/cleanup/", CleanupJobsView.as_view()),
    path("api/v1/jobs/<str:job_id>/", JobStatusView.as_view()),
    path("api/v1/jobs/<str:job_id>/result/", JobResultView.as_view()),
    path("api/v1/health/", HealthView.as_view()),
    path("api/v1/config/file-types/", FileConfigView.as_view()),
]
