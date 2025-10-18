from django.urls import path

from .views import CompareCandidatesView, ExplainMatchView, InterviewQuestionsView

urlpatterns = [
    path("explain-match/", ExplainMatchView.as_view(), name="rag_explain_match"),
    path("compare/", CompareCandidatesView.as_view(), name="rag_compare"),
    path("interview-questions/", InterviewQuestionsView.as_view(), name="rag_interview_questions"),
]
