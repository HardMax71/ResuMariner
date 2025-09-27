from django.urls import path

from .views import DeleteResumeView, GetResumeView, StoreVectorsView, UpsertResumeView

urlpatterns = [
    path("resume", UpsertResumeView.as_view()),
    path("resume/<str:resume_id>", GetResumeView.as_view()),
    path("vectors", StoreVectorsView.as_view()),
    path("resume/<str:resume_id>/delete", DeleteResumeView.as_view()),
]

