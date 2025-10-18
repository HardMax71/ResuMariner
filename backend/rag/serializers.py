from rest_framework import serializers


class ExplainMatchRequestSerializer(serializers.Serializer):
    resume_uid = serializers.CharField(required=True)
    job_description = serializers.CharField(required=True, min_length=50, max_length=10000)


class CompareCandidatesRequestSerializer(serializers.Serializer):
    resume_uids = serializers.ListField(child=serializers.CharField(), min_length=2, max_length=5)
    criteria = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False, allow_null=True, max_length=20
    )
    job_context = serializers.CharField(required=False, allow_null=True, max_length=5000)


class InterviewQuestionsRequestSerializer(serializers.Serializer):
    resume_uid = serializers.CharField(required=True)
    interview_type = serializers.ChoiceField(choices=["technical", "behavioral", "general"], default="technical")
    role_context = serializers.CharField(required=False, allow_null=True, max_length=5000)
    focus_areas = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False, allow_null=True, max_length=20
    )
