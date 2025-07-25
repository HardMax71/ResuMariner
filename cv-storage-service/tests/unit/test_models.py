"""Comprehensive tests for cv-storage-service models to achieve 95%+ coverage."""

import pytest
from pydantic import ValidationError
from cv_storage_service.models.storage_models import (
    StoreRequest,
    StoreResponse,
    VectorPayload,
    VectorStoreRequest,
    VectorStoreResponse,
)


class TestStoreRequest:
    """Test StoreRequest model"""

    def test_store_request_valid_data(self):
        """Test StoreRequest with valid data"""
        cv_data = {
            "personal_info": {
                "contact": {"email": "test@example.com", "phone": "+1234567890"},
                "name": "John Doe",
            },
            "experience": [],
            "education": [],
        }

        request = StoreRequest(job_id="job-123", cv_data=cv_data)

        assert request.job_id == "job-123"
        assert request.cv_data == cv_data
        assert (
            request.cv_data["personal_info"]["contact"]["email"] == "test@example.com"
        )

    def test_store_request_missing_job_id(self):
        """Test StoreRequest with missing job_id"""
        cv_data = {"personal_info": {"contact": {"email": "test@example.com"}}}

        with pytest.raises(ValidationError) as exc_info:
            StoreRequest(cv_data=cv_data)

        assert "job_id" in str(exc_info.value)

    def test_store_request_missing_cv_data(self):
        """Test StoreRequest with missing cv_data"""
        with pytest.raises(ValidationError) as exc_info:
            StoreRequest(job_id="job-123")

        assert "cv_data" in str(exc_info.value)

    def test_store_request_empty_cv_data(self):
        """Test StoreRequest with empty cv_data"""
        with pytest.raises(ValidationError) as exc_info:
            StoreRequest(job_id="job-123", cv_data={})

        assert "CV data cannot be empty" in str(exc_info.value)

    def test_store_request_missing_personal_info(self):
        """Test StoreRequest with missing personal_info"""
        cv_data = {"experience": [], "education": []}

        with pytest.raises(ValidationError) as exc_info:
            StoreRequest(job_id="job-123", cv_data=cv_data)

        assert "CV data must contain personal_info section" in str(exc_info.value)

    def test_store_request_missing_contact(self):
        """Test StoreRequest with missing contact in personal_info"""
        cv_data = {"personal_info": {"name": "John Doe"}}

        with pytest.raises(ValidationError) as exc_info:
            StoreRequest(job_id="job-123", cv_data=cv_data)

        assert "CV data must contain personal_info.contact section" in str(
            exc_info.value
        )

    def test_store_request_empty_contact(self):
        """Test StoreRequest with empty contact section"""
        cv_data = {"personal_info": {"contact": {}, "name": "John Doe"}}

        with pytest.raises(ValidationError) as exc_info:
            StoreRequest(job_id="job-123", cv_data=cv_data)

        assert "CV data must contain personal_info.contact.email" in str(exc_info.value)

    def test_store_request_missing_email(self):
        """Test StoreRequest with missing email in contact"""
        cv_data = {
            "personal_info": {"contact": {"phone": "+1234567890"}, "name": "John Doe"}
        }

        with pytest.raises(ValidationError) as exc_info:
            StoreRequest(job_id="job-123", cv_data=cv_data)

        assert "CV data must contain personal_info.contact.email" in str(exc_info.value)

    def test_store_request_complex_cv_data(self):
        """Test StoreRequest with complex CV data"""
        cv_data = {
            "personal_info": {
                "contact": {
                    "email": "complex@example.com",
                    "phone": "+1234567890",
                    "linkedin": "https://linkedin.com/in/complex",
                },
                "name": "Complex User",
                "title": "Senior Developer",
            },
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Developer",
                    "duration": "2020-2023",
                }
            ],
            "education": [
                {"institution": "University", "degree": "CS", "year": "2020"}
            ],
            "skills": ["Python", "FastAPI", "PostgreSQL"],
        }

        request = StoreRequest(job_id="complex-job-456", cv_data=cv_data)

        assert request.job_id == "complex-job-456"
        assert len(request.cv_data["experience"]) == 1
        assert len(request.cv_data["education"]) == 1
        assert len(request.cv_data["skills"]) == 3

    def test_store_request_field_descriptions(self):
        """Test StoreRequest field descriptions"""
        schema = StoreRequest.schema()
        properties = schema["properties"]

        assert (
            properties["job_id"]["description"]
            == "Unique identifier for the CV processing job"
        )
        assert properties["cv_data"]["description"] == "Structured CV data"

    def test_store_request_json_serialization(self):
        """Test StoreRequest JSON serialization"""
        cv_data = {"personal_info": {"contact": {"email": "json@example.com"}}}

        request = StoreRequest(job_id="json-job", cv_data=cv_data)

        json_data = request.model_dump()
        assert json_data["job_id"] == "json-job"
        assert (
            json_data["cv_data"]["personal_info"]["contact"]["email"]
            == "json@example.com"
        )

    def test_cv_data_validator_directly(self):
        """Test cv_data validator function directly"""
        # Test valid data
        valid_data = {"personal_info": {"contact": {"email": "direct@example.com"}}}
        result = StoreRequest.validate_cv_data(valid_data)
        assert result == valid_data

        # Test empty data
        with pytest.raises(ValueError) as exc_info:
            StoreRequest.validate_cv_data({})
        assert "CV data cannot be empty" in str(exc_info.value)


class TestStoreResponse:
    """Test StoreResponse model"""

    def test_store_response_valid_data(self):
        """Test StoreResponse with valid data"""
        response = StoreResponse(graph_id="graph-123", vector_count=5)

        assert response.graph_id == "graph-123"
        assert response.vector_count == 5

    def test_store_response_default_vector_count(self):
        """Test StoreResponse with default vector_count"""
        response = StoreResponse(graph_id="graph-456")

        assert response.graph_id == "graph-456"
        assert response.vector_count == 0

    def test_store_response_missing_graph_id(self):
        """Test StoreResponse with missing graph_id"""
        with pytest.raises(ValidationError) as exc_info:
            StoreResponse(vector_count=3)

        assert "graph_id" in str(exc_info.value)

    def test_store_response_field_descriptions(self):
        """Test StoreResponse field descriptions"""
        schema = StoreResponse.schema()
        properties = schema["properties"]

        assert (
            properties["graph_id"]["description"]
            == "ID of the CV in the graph database"
        )
        assert (
            properties["vector_count"]["description"]
            == "Number of vector embeddings stored"
        )

    def test_store_response_json_serialization(self):
        """Test StoreResponse JSON serialization"""
        response = StoreResponse(graph_id="json-graph-789", vector_count=10)

        json_data = response.model_dump()
        assert json_data["graph_id"] == "json-graph-789"
        assert json_data["vector_count"] == 10


class TestVectorPayload:
    """Test VectorPayload model"""

    def test_vector_payload_valid_data(self):
        """Test VectorPayload with valid data"""
        payload = VectorPayload(
            vector=[0.1, 0.2, 0.3],
            text="Sample text for embedding",
            person_name="John Doe",
            email="john@example.com",
            source="employment",
            context="Previous work experience",
        )

        assert payload.vector == [0.1, 0.2, 0.3]
        assert payload.text == "Sample text for embedding"
        assert payload.person_name == "John Doe"
        assert payload.email == "john@example.com"
        assert payload.source == "employment"
        assert payload.context == "Previous work experience"

    def test_vector_payload_required_fields_only(self):
        """Test VectorPayload with only required fields"""
        payload = VectorPayload(
            vector=[0.5, 0.6, 0.7], text="Minimal text", source="project"
        )

        assert payload.vector == [0.5, 0.6, 0.7]
        assert payload.text == "Minimal text"
        assert payload.source == "project"
        assert payload.person_name is None
        assert payload.email is None
        assert payload.context is None

    def test_vector_payload_missing_vector(self):
        """Test VectorPayload with missing vector"""
        with pytest.raises(ValidationError) as exc_info:
            VectorPayload(text="Text without vector", source="test")

        assert "vector" in str(exc_info.value)

    def test_vector_payload_missing_text(self):
        """Test VectorPayload with missing text"""
        with pytest.raises(ValidationError) as exc_info:
            VectorPayload(vector=[0.1, 0.2], source="test")

        assert "text" in str(exc_info.value)

    def test_vector_payload_missing_source(self):
        """Test VectorPayload with missing source"""
        with pytest.raises(ValidationError) as exc_info:
            VectorPayload(vector=[0.1, 0.2], text="Text without source")

        assert "source" in str(exc_info.value)

    def test_vector_payload_empty_vector(self):
        """Test VectorPayload with empty vector"""
        payload = VectorPayload(vector=[], text="Empty vector text", source="test")

        assert payload.vector == []

    def test_vector_payload_large_vector(self):
        """Test VectorPayload with large vector"""
        large_vector = [0.1] * 1000
        payload = VectorPayload(
            vector=large_vector, text="Large vector text", source="test"
        )

        assert len(payload.vector) == 1000
        assert all(v == 0.1 for v in payload.vector)

    def test_vector_payload_field_descriptions(self):
        """Test VectorPayload field descriptions"""
        schema = VectorPayload.schema()
        properties = schema["properties"]

        assert properties["vector"]["description"] == "Vector embedding"
        assert properties["text"]["description"] == "Text that was embedded"
        assert properties["person_name"]["description"] == "Person name"
        assert properties["email"]["description"] == "Email address"
        assert (
            properties["source"]["description"]
            == "Source of text (employment, project, etc.)"
        )
        assert properties["context"]["description"] == "Context for the text"


class TestVectorStoreRequest:
    """Test VectorStoreRequest model"""

    def test_vector_store_request_valid_data(self):
        """Test VectorStoreRequest with valid data"""
        vectors = [
            VectorPayload(vector=[0.1, 0.2], text="First text", source="employment"),
            VectorPayload(vector=[0.3, 0.4], text="Second text", source="education"),
        ]

        request = VectorStoreRequest(cv_id="cv-123", vectors=vectors)

        assert request.cv_id == "cv-123"
        assert len(request.vectors) == 2
        assert request.vectors[0].text == "First text"
        assert request.vectors[1].text == "Second text"

    def test_vector_store_request_empty_vectors(self):
        """Test VectorStoreRequest with empty vectors list"""
        request = VectorStoreRequest(cv_id="cv-456", vectors=[])

        assert request.cv_id == "cv-456"
        assert len(request.vectors) == 0

    def test_vector_store_request_missing_cv_id(self):
        """Test VectorStoreRequest with missing cv_id"""
        vectors = [VectorPayload(vector=[0.1], text="Text", source="test")]

        with pytest.raises(ValidationError) as exc_info:
            VectorStoreRequest(vectors=vectors)

        assert "cv_id" in str(exc_info.value)

    def test_vector_store_request_missing_vectors(self):
        """Test VectorStoreRequest with missing vectors"""
        with pytest.raises(ValidationError) as exc_info:
            VectorStoreRequest(cv_id="cv-789")

        assert "vectors" in str(exc_info.value)

    def test_vector_store_request_field_descriptions(self):
        """Test VectorStoreRequest field descriptions"""
        schema = VectorStoreRequest.schema()
        properties = schema["properties"]

        assert properties["cv_id"]["description"] == "CV identifier"
        assert properties["vectors"]["description"] == "List of vectors with metadata"

    def test_vector_store_request_complex_vectors(self):
        """Test VectorStoreRequest with complex vector data"""
        vectors = [
            VectorPayload(
                vector=[0.1, 0.2, 0.3, 0.4],
                text="Complex employment history at Tech Corp",
                person_name="Jane Smith",
                email="jane@example.com",
                source="employment",
                context="Senior software engineer role",
            ),
            VectorPayload(
                vector=[0.5, 0.6, 0.7, 0.8],
                text="Master's degree in Computer Science",
                person_name="Jane Smith",
                email="jane@example.com",
                source="education",
                context="Graduate studies with focus on AI",
            ),
        ]

        request = VectorStoreRequest(cv_id="complex-cv-101", vectors=vectors)

        assert request.cv_id == "complex-cv-101"
        assert len(request.vectors) == 2
        assert all(v.person_name == "Jane Smith" for v in request.vectors)
        assert all(v.email == "jane@example.com" for v in request.vectors)


class TestVectorStoreResponse:
    """Test VectorStoreResponse model"""

    def test_vector_store_response_valid_data(self):
        """Test VectorStoreResponse with valid data"""
        response = VectorStoreResponse(status="success", vector_count=15)

        assert response.status == "success"
        assert response.vector_count == 15

    def test_vector_store_response_default_status(self):
        """Test VectorStoreResponse with default status"""
        response = VectorStoreResponse(vector_count=8)

        assert response.status == "success"
        assert response.vector_count == 8

    def test_vector_store_response_custom_status(self):
        """Test VectorStoreResponse with custom status"""
        response = VectorStoreResponse(status="partial", vector_count=3)

        assert response.status == "partial"
        assert response.vector_count == 3

    def test_vector_store_response_missing_vector_count(self):
        """Test VectorStoreResponse with missing vector_count"""
        with pytest.raises(ValidationError) as exc_info:
            VectorStoreResponse(status="success")

        assert "vector_count" in str(exc_info.value)

    def test_vector_store_response_zero_vector_count(self):
        """Test VectorStoreResponse with zero vector count"""
        response = VectorStoreResponse(status="empty", vector_count=0)

        assert response.status == "empty"
        assert response.vector_count == 0

    def test_vector_store_response_field_descriptions(self):
        """Test VectorStoreResponse field descriptions"""
        schema = VectorStoreResponse.schema()
        properties = schema["properties"]

        assert properties["status"]["description"] == "Operation status"
        assert properties["vector_count"]["description"] == "Number of vectors stored"

    def test_vector_store_response_json_serialization(self):
        """Test VectorStoreResponse JSON serialization"""
        response = VectorStoreResponse(status="completed", vector_count=25)

        json_data = response.model_dump()
        assert json_data["status"] == "completed"
        assert json_data["vector_count"] == 25


class TestModelIntegration:
    """Test integration between models"""

    def test_store_request_to_vector_store_request(self):
        """Test converting StoreRequest data to VectorStoreRequest"""
        cv_data = {
            "personal_info": {
                "contact": {"email": "integration@example.com"},
                "name": "Integration User",
            }
        }

        StoreRequest(job_id="integration-job", cv_data=cv_data)

        # Simulate creating vectors from store request
        vectors = [
            VectorPayload(
                vector=[0.1, 0.2],
                text="Integration User",
                person_name="Integration User",
                email="integration@example.com",
                source="personal_info",
            )
        ]

        vector_request = VectorStoreRequest(cv_id="integration-cv", vectors=vectors)

        assert vector_request.cv_id == "integration-cv"
        assert len(vector_request.vectors) == 1
        assert vector_request.vectors[0].email == "integration@example.com"

    def test_all_models_json_compatible(self):
        """Test all models are JSON serializable"""
        # Create instances of all models
        cv_data = {"personal_info": {"contact": {"email": "json@example.com"}}}

        store_request = StoreRequest(job_id="json-job", cv_data=cv_data)
        store_response = StoreResponse(graph_id="json-graph", vector_count=5)

        vector_payload = VectorPayload(
            vector=[0.1, 0.2], text="JSON text", source="json_test"
        )

        vector_store_request = VectorStoreRequest(
            cv_id="json-cv", vectors=[vector_payload]
        )

        vector_store_response = VectorStoreResponse(
            status="json_success", vector_count=1
        )

        # All should serialize to JSON without errors
        models = [
            store_request,
            store_response,
            vector_payload,
            vector_store_request,
            vector_store_response,
        ]

        for model in models:
            json_data = model.model_dump()
            assert isinstance(json_data, dict)
            assert len(json_data) > 0

    def test_model_validation_consistency(self):
        """Test validation consistency across models"""
        # All models should raise ValidationError for missing required fields
        with pytest.raises(ValidationError):
            StoreRequest(job_id="test")  # Missing cv_data

        with pytest.raises(ValidationError):
            StoreResponse()  # Missing graph_id

        with pytest.raises(ValidationError):
            VectorPayload(vector=[0.1])  # Missing text and source

        with pytest.raises(ValidationError):
            VectorStoreRequest(cv_id="test")  # Missing vectors

        with pytest.raises(ValidationError):
            VectorStoreResponse(status="test")  # Missing vector_count
