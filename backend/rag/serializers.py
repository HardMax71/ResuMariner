from rest_framework import serializers


class ExplainMatchRequestSerializer(serializers.Serializer):
    resume_uid = serializers.CharField(required=True)
    job_description = serializers.CharField(required=True, min_length=50)


class CompareCandidatesRequestSerializer(serializers.Serializer):
    resume_uids = serializers.ListField(child=serializers.CharField(), min_length=2, max_length=5)
    criteria = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    job_context = serializers.CharField(required=False, allow_null=True)


class InterviewQuestionsRequestSerializer(serializers.Serializer):
    resume_uid = serializers.CharField(required=True)
    interview_type = serializers.ChoiceField(choices=["technical", "behavioral", "general"], default="technical")
    role_context = serializers.CharField(required=False, allow_null=True)
    focus_areas = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
