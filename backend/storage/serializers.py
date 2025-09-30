from rest_framework import serializers


class UpsertResumeRequestSerializer(serializers.Serializer):
    job_id = serializers.CharField(min_length=1)
    resume_data = serializers.DictField(child=serializers.JSONField())


class UpsertResumeResponseSerializer(serializers.Serializer):
    graph_id = serializers.CharField()
    operation = serializers.CharField()
    previous_id = serializers.CharField(allow_null=True, required=False)
    vector_count = serializers.IntegerField()


class VectorPayloadSerializer(serializers.Serializer):
    vector = serializers.ListField(child=serializers.FloatField(), allow_empty=False)
    text = serializers.CharField()
    name = serializers.CharField(allow_null=True, required=False)
    email = serializers.CharField(allow_null=True, required=False)
    source = serializers.CharField()  # type: ignore[assignment]
    context = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # type: ignore[assignment]


class VectorStoreRequestSerializer(serializers.Serializer):
    resume_id = serializers.CharField()
    vectors = serializers.ListField(child=VectorPayloadSerializer())


class VectorStoreResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    vector_count = serializers.IntegerField()
