"""Comprehensive tests for cv-processing-service models to achieve 95%+ coverage."""

import pytest
from pydantic import ValidationError
from models.processing_models import ParserType, ProcessingOptions, ProcessingResult


class TestParserType:
    """Test ParserType enum"""

    def test_parser_type_values(self):
        """Test ParserType enum values"""
        assert ParserType.PDF == "pdf"
        assert ParserType.IMAGE == "image"
        assert ParserType.DOCX == "docx"

    def test_parser_type_string_conversion(self):
        """Test ParserType string conversion"""
        assert str(ParserType.PDF) == "pdf"
        assert str(ParserType.IMAGE) == "image"
        assert str(ParserType.DOCX) == "docx"

    def test_parser_type_enum_iteration(self):
        """Test ParserType enum iteration"""
        expected_values = {"pdf", "image", "docx"}
        actual_values = {parser_type.value for parser_type in ParserType}
        assert actual_values == expected_values

    def test_parser_type_equality(self):
        """Test ParserType equality comparisons"""
        assert ParserType.PDF == ParserType.PDF
        assert ParserType.PDF != ParserType.IMAGE
        assert ParserType("pdf") == ParserType.PDF

    def test_parser_type_from_string(self):
        """Test creating ParserType from string"""
        assert ParserType("pdf") == ParserType.PDF
        assert ParserType("image") == ParserType.IMAGE
        assert ParserType("docx") == ParserType.DOCX

    def test_parser_type_invalid_value(self):
        """Test ParserType with invalid value"""
        with pytest.raises(ValueError):
            ParserType("invalid")


class TestProcessingOptions:
    """Test ProcessingOptions model"""

    def test_processing_options_defaults(self):
        """Test ProcessingOptions default values"""
        options = ProcessingOptions()

        assert options.parallel is False
        assert options.generate_review is True
        assert options.store_in_db is True

    def test_processing_options_custom_values(self):
        """Test ProcessingOptions with custom values"""
        options = ProcessingOptions(
            parallel=True, generate_review=False, store_in_db=False
        )

        assert options.parallel is True
        assert options.generate_review is False
        assert options.store_in_db is False

    def test_processing_options_partial_custom(self):
        """Test ProcessingOptions with partial custom values"""
        options = ProcessingOptions(parallel=True)

        assert options.parallel is True
        assert options.generate_review is True  # Default
        assert options.store_in_db is True  # Default

    def test_processing_options_from_dict(self):
        """Test creating ProcessingOptions from dictionary"""
        data = {"parallel": True, "generate_review": False, "store_in_db": True}

        options = ProcessingOptions(**data)
        assert options.parallel is True
        assert options.generate_review is False
        assert options.store_in_db is True

    def test_processing_options_serialization(self):
        """Test ProcessingOptions serialization"""
        options = ProcessingOptions(parallel=True, generate_review=False)

        # Test model_dump
        data = options.model_dump()
        expected = {"parallel": True, "generate_review": False, "store_in_db": True}
        assert data == expected

    def test_processing_options_json_serialization(self):
        """Test ProcessingOptions JSON serialization"""
        options = ProcessingOptions(parallel=True)

        json_str = options.model_dump_json()
        assert isinstance(json_str, str)
        assert "parallel" in json_str
        assert "true" in json_str.lower()

    def test_processing_options_field_descriptions(self):
        """Test ProcessingOptions field descriptions"""
        schema = ProcessingOptions.model_json_schema()

        assert "description" in schema["properties"]["parallel"]
        assert "description" in schema["properties"]["generate_review"]
        assert "description" in schema["properties"]["store_in_db"]

        assert "parallel processing" in schema["properties"]["parallel"]["description"]
        assert "review" in schema["properties"]["generate_review"]["description"]
        assert "database" in schema["properties"]["store_in_db"]["description"]

    def test_processing_options_type_validation(self):
        """Test ProcessingOptions type validation"""
        # Valid boolean values
        valid_values = [True, False, 1, 0, "true", "false", "1", "0"]

        for value in valid_values:
            options = ProcessingOptions(parallel=value)
            assert isinstance(options.parallel, bool)

    def test_processing_options_equality(self):
        """Test ProcessingOptions equality"""
        options1 = ProcessingOptions(parallel=True, generate_review=False)
        options2 = ProcessingOptions(parallel=True, generate_review=False)
        options3 = ProcessingOptions(parallel=False, generate_review=False)

        assert options1 == options2
        assert options1 != options3

    def test_processing_options_copy(self):
        """Test ProcessingOptions copying"""
        original = ProcessingOptions(parallel=True, generate_review=False)

        # Test model_copy
        copied = original.model_copy()
        assert copied == original
        assert copied is not original

        # Test model_copy with updates
        updated = original.model_copy(update={"parallel": False})
        assert updated.parallel is False
        assert updated.generate_review is False
        assert original.parallel is True  # Original unchanged


class TestProcessingResult:
    """Test ProcessingResult model"""

    def test_processing_result_creation(self):
        """Test ProcessingResult creation"""
        structured_data = {"name": "John Doe", "skills": ["Python", "FastAPI"]}
        review = {"score": 85, "feedback": "Good candidate"}
        processing_time = 12.5
        metadata = {"parser": "pdf", "pages": 2}

        result = ProcessingResult(
            structured_data=structured_data,
            review=review,
            processing_time=processing_time,
            metadata=metadata,
        )

        assert result.structured_data == structured_data
        assert result.review == review
        assert result.processing_time == processing_time
        assert result.metadata == metadata

    def test_processing_result_minimal(self):
        """Test ProcessingResult with minimal required fields"""
        structured_data = {"name": "Jane Doe"}
        processing_time = 5.0

        result = ProcessingResult(
            structured_data=structured_data, processing_time=processing_time
        )

        assert result.structured_data == structured_data
        assert result.processing_time == processing_time
        assert result.review is None
        assert result.metadata == {}

    def test_processing_result_default_metadata(self):
        """Test ProcessingResult default metadata factory"""
        result1 = ProcessingResult(
            structured_data={"name": "Person 1"}, processing_time=1.0
        )
        result2 = ProcessingResult(
            structured_data={"name": "Person 2"}, processing_time=2.0
        )

        # Each instance should have its own metadata dict
        result1.metadata["key1"] = "value1"
        result2.metadata["key2"] = "value2"

        assert "key1" in result1.metadata
        assert "key1" not in result2.metadata
        assert "key2" in result2.metadata
        assert "key2" not in result1.metadata

    def test_processing_result_validation_errors(self):
        """Test ProcessingResult validation errors"""
        # Missing required field
        with pytest.raises(ValidationError):
            ProcessingResult(
                structured_data={"name": "Test"}
            )  # Missing processing_time

        with pytest.raises(ValidationError):
            ProcessingResult(processing_time=1.0)  # Missing structured_data

    def test_processing_result_type_validation(self):
        """Test ProcessingResult type validation"""
        # Invalid structured_data type
        with pytest.raises(ValidationError):
            ProcessingResult(structured_data="not a dict", processing_time=1.0)

        # Invalid processing_time type
        with pytest.raises(ValidationError):
            ProcessingResult(
                structured_data={"name": "Test"}, processing_time="not a number"
            )

    def test_processing_result_serialization(self):
        """Test ProcessingResult serialization"""
        structured_data = {"name": "Test User", "skills": ["Python"]}
        review = {"score": 90}

        result = ProcessingResult(
            structured_data=structured_data,
            review=review,
            processing_time=10.5,
            metadata={"source": "test"},
        )

        data = result.model_dump()

        assert data["structured_data"] == structured_data
        assert data["review"] == review
        assert data["processing_time"] == 10.5
        assert data["metadata"] == {"source": "test"}

    def test_processing_result_json_serialization(self):
        """Test ProcessingResult JSON serialization"""
        result = ProcessingResult(structured_data={"name": "Test"}, processing_time=5.5)

        json_str = result.model_dump_json()
        assert isinstance(json_str, str)
        assert "structured_data" in json_str
        assert "processing_time" in json_str

    def test_processing_result_complex_data(self):
        """Test ProcessingResult with complex nested data"""
        structured_data = {
            "personal_info": {
                "name": "John Doe",
                "contact": {"email": "john@example.com", "phone": "+1234567890"},
            },
            "work_experience": [
                {"company": "Tech Corp", "position": "Developer", "years": [2020, 2023]}
            ],
            "skills": ["Python", "FastAPI", "PostgreSQL"],
        }

        review = {
            "overall_score": 85,
            "strengths": ["Strong technical skills", "Good experience"],
            "areas_for_improvement": ["Could add more projects"],
            "recommendation": "hire",
        }

        result = ProcessingResult(
            structured_data=structured_data,
            review=review,
            processing_time=15.7,
            metadata={
                "parser_version": "1.0.0",
                "confidence_scores": {"extraction": 0.95, "classification": 0.88},
            },
        )

        assert result.structured_data["personal_info"]["name"] == "John Doe"
        assert len(result.structured_data["work_experience"]) == 1
        assert result.review["overall_score"] == 85
        assert result.metadata["parser_version"] == "1.0.0"

    def test_processing_result_none_review(self):
        """Test ProcessingResult with None review"""
        result = ProcessingResult(
            structured_data={"name": "Test"}, processing_time=1.0, review=None
        )

        assert result.review is None

        # Serialization should handle None properly
        data = result.model_dump()
        assert data["review"] is None

    def test_processing_result_field_types(self):
        """Test ProcessingResult field type annotations"""
        from typing import get_type_hints

        hints = get_type_hints(ProcessingResult)

        # Check that type hints are correctly set
        assert "structured_data" in hints
        assert "review" in hints
        assert "processing_time" in hints
        assert "metadata" in hints

    def test_processing_result_immutability_pattern(self):
        """Test ProcessingResult can be made immutable if needed"""
        result = ProcessingResult(structured_data={"name": "Test"}, processing_time=1.0)

        # Test that we can create a copy with updates
        updated = result.model_copy(update={"processing_time": 2.0})

        assert result.processing_time == 1.0
        assert updated.processing_time == 2.0
