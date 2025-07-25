"""Comprehensive tests for cv-storage-service utils to achieve 95%+ coverage."""

from cv_storage_service.utils.errors import (
    StorageServiceError,
    GraphDBError,
    VectorDBError,
    InvalidDataError,
    DatabaseConnectionError,
)


class TestStorageServiceError:
    """Test StorageServiceError base class"""

    def test_storage_service_error_basic(self):
        """Test basic StorageServiceError creation"""
        error = StorageServiceError("Base storage error")

        assert str(error) == "Base storage error"
        assert error.message == "Base storage error"
        assert error.error_code is None
        assert error.details == {}

    def test_storage_service_error_with_details(self):
        """Test StorageServiceError with error code and details"""
        details = {"key": "value", "number": 42}
        error = StorageServiceError(
            "Detailed error", error_code="E001", details=details
        )

        assert error.message == "Detailed error"
        assert error.error_code == "E001"
        assert error.details == details

    def test_storage_service_error_to_dict(self):
        """Test StorageServiceError to_dict method"""
        error = StorageServiceError(
            "Dict test error", error_code="E002", details={"test": "data"}
        )

        result = error.to_dict()

        expected = {
            "error_type": "StorageServiceError",
            "message": "Dict test error",
            "error_code": "E002",
            "details": {"test": "data"},
        }

        assert result == expected

    def test_storage_service_error_empty_details(self):
        """Test StorageServiceError with None details becomes empty dict"""
        error = StorageServiceError("Test", details=None)

        assert error.details == {}

    def test_storage_service_error_inheritance(self):
        """Test StorageServiceError inherits from Exception"""
        error = StorageServiceError("Inheritance test")

        assert isinstance(error, Exception)
        assert isinstance(error, StorageServiceError)


class TestGraphDBError:
    """Test GraphDBError class"""

    def test_graph_db_error_basic(self):
        """Test basic GraphDBError creation"""
        error = GraphDBError("Graph database failed")

        assert str(error) == "Graph database failed"
        assert error.message == "Graph database failed"
        assert isinstance(error, StorageServiceError)
        assert error.operation is None
        assert error.node_type is None

    def test_graph_db_error_with_operation(self):
        """Test GraphDBError with operation"""
        error = GraphDBError("Operation failed", operation="create_node")

        assert error.operation == "create_node"
        assert error.details["operation"] == "create_node"

    def test_graph_db_error_with_node_type(self):
        """Test GraphDBError with node type"""
        error = GraphDBError("Node creation failed", node_type="CVNode")

        assert error.node_type == "CVNode"
        assert error.details["node_type"] == "CVNode"

    def test_graph_db_error_with_all_params(self):
        """Test GraphDBError with all parameters"""
        error = GraphDBError(
            "Complex graph error",
            operation="update_relationship",
            node_type="PersonNode",
            error_code="G001",
        )

        assert error.message == "Complex graph error"
        assert error.operation == "update_relationship"
        assert error.node_type == "PersonNode"
        assert error.error_code == "G001"
        assert error.details["operation"] == "update_relationship"
        assert error.details["node_type"] == "PersonNode"

    def test_graph_db_error_to_dict(self):
        """Test GraphDBError to_dict method"""
        error = GraphDBError("Graph dict test", operation="query", node_type="TestNode")

        result = error.to_dict()

        assert result["error_type"] == "GraphDBError"
        assert result["message"] == "Graph dict test"
        assert result["details"]["operation"] == "query"
        assert result["details"]["node_type"] == "TestNode"


class TestVectorDBError:
    """Test VectorDBError class"""

    def test_vector_db_error_basic(self):
        """Test basic VectorDBError creation"""
        error = VectorDBError("Vector database failed")

        assert str(error) == "Vector database failed"
        assert error.message == "Vector database failed"
        assert isinstance(error, StorageServiceError)
        assert error.collection_name is None
        assert error.vector_size is None

    def test_vector_db_error_with_collection(self):
        """Test VectorDBError with collection name"""
        error = VectorDBError("Collection error", collection_name="cv_embeddings")

        assert error.collection_name == "cv_embeddings"
        assert error.details["collection_name"] == "cv_embeddings"

    def test_vector_db_error_with_vector_size(self):
        """Test VectorDBError with vector size"""
        error = VectorDBError("Vector size mismatch", vector_size=384)

        assert error.vector_size == 384
        assert error.details["vector_size"] == 384

    def test_vector_db_error_with_all_params(self):
        """Test VectorDBError with all parameters"""
        error = VectorDBError(
            "Complex vector error",
            collection_name="test_collection",
            vector_size=512,
            error_code="V001",
        )

        assert error.message == "Complex vector error"
        assert error.collection_name == "test_collection"
        assert error.vector_size == 512
        assert error.error_code == "V001"
        assert error.details["collection_name"] == "test_collection"
        assert error.details["vector_size"] == 512

    def test_vector_db_error_to_dict(self):
        """Test VectorDBError to_dict method"""
        error = VectorDBError(
            "Vector dict test", collection_name="dict_test", vector_size=256
        )

        result = error.to_dict()

        assert result["error_type"] == "VectorDBError"
        assert result["message"] == "Vector dict test"
        assert result["details"]["collection_name"] == "dict_test"
        assert result["details"]["vector_size"] == 256


class TestInvalidDataError:
    """Test InvalidDataError class"""

    def test_invalid_data_error_basic(self):
        """Test basic InvalidDataError creation"""
        error = InvalidDataError("Invalid data provided")

        assert str(error) == "Invalid data provided"
        assert error.message == "Invalid data provided"
        assert isinstance(error, StorageServiceError)
        assert error.data_type is None
        assert error.validation_errors == []

    def test_invalid_data_error_with_data_type(self):
        """Test InvalidDataError with data type"""
        error = InvalidDataError("Invalid CV data", data_type="cv_structure")

        assert error.data_type == "cv_structure"
        assert error.details["data_type"] == "cv_structure"

    def test_invalid_data_error_with_validation_errors(self):
        """Test InvalidDataError with validation errors"""
        validation_errors = [
            "Missing required field: email",
            "Invalid date format in experience",
            "Empty skills list",
        ]

        error = InvalidDataError(
            "Validation failed", validation_errors=validation_errors
        )

        assert error.validation_errors == validation_errors
        assert error.details["validation_errors"] == validation_errors

    def test_invalid_data_error_empty_validation_errors(self):
        """Test InvalidDataError with None validation errors becomes empty list"""
        error = InvalidDataError("Test", validation_errors=None)

        assert error.validation_errors == []

    def test_invalid_data_error_with_all_params(self):
        """Test InvalidDataError with all parameters"""
        validation_errors = ["Error 1", "Error 2"]

        error = InvalidDataError(
            "Complete validation failure",
            data_type="resume_data",
            validation_errors=validation_errors,
            error_code="D001",
        )

        assert error.message == "Complete validation failure"
        assert error.data_type == "resume_data"
        assert error.validation_errors == validation_errors
        assert error.error_code == "D001"
        assert error.details["data_type"] == "resume_data"
        assert error.details["validation_errors"] == validation_errors

    def test_invalid_data_error_to_dict(self):
        """Test InvalidDataError to_dict method"""
        error = InvalidDataError(
            "Data dict test", data_type="test_type", validation_errors=["test error"]
        )

        result = error.to_dict()

        assert result["error_type"] == "InvalidDataError"
        assert result["message"] == "Data dict test"
        assert result["details"]["data_type"] == "test_type"
        assert result["details"]["validation_errors"] == ["test error"]


class TestDatabaseConnectionError:
    """Test DatabaseConnectionError class"""

    def test_database_connection_error_basic(self):
        """Test basic DatabaseConnectionError creation"""
        error = DatabaseConnectionError("Failed to connect to database")

        assert str(error) == "Failed to connect to database"
        assert error.message == "Failed to connect to database"
        assert isinstance(error, StorageServiceError)
        assert error.database_type is None
        assert error.connection_string is None

    def test_database_connection_error_with_database_type(self):
        """Test DatabaseConnectionError with database type"""
        error = DatabaseConnectionError(
            "Neo4j connection failed", database_type="neo4j"
        )

        assert error.database_type == "neo4j"
        assert error.details["database_type"] == "neo4j"

    def test_database_connection_error_with_connection_string(self):
        """Test DatabaseConnectionError with connection string"""
        error = DatabaseConnectionError(
            "Connection failed", connection_string="bolt://user:pass@localhost:7687"
        )

        assert error.connection_string == "bolt://user:pass@localhost:7687"
        # Connection string should be redacted in details
        assert error.details["connection_string"] == "[REDACTED]"

    def test_database_connection_error_with_all_params(self):
        """Test DatabaseConnectionError with all parameters"""
        error = DatabaseConnectionError(
            "Complete connection failure",
            database_type="qdrant",
            connection_string="http://localhost:6333",
            error_code="C001",
        )

        assert error.message == "Complete connection failure"
        assert error.database_type == "qdrant"
        assert error.connection_string == "http://localhost:6333"
        assert error.error_code == "C001"
        assert error.details["database_type"] == "qdrant"
        assert error.details["connection_string"] == "[REDACTED]"

    def test_database_connection_error_to_dict(self):
        """Test DatabaseConnectionError to_dict method"""
        error = DatabaseConnectionError(
            "Connection dict test",
            database_type="test_db",
            connection_string="secret://connection:string",
        )

        result = error.to_dict()

        assert result["error_type"] == "DatabaseConnectionError"
        assert result["message"] == "Connection dict test"
        assert result["details"]["database_type"] == "test_db"
        assert result["details"]["connection_string"] == "[REDACTED]"


class TestErrorInheritance:
    """Test error class inheritance and relationships"""

    def test_all_errors_inherit_from_storage_service_error(self):
        """Test all custom errors inherit from StorageServiceError"""
        error_classes = [
            GraphDBError,
            VectorDBError,
            InvalidDataError,
            DatabaseConnectionError,
        ]

        for error_class in error_classes:
            assert issubclass(error_class, StorageServiceError)
            assert issubclass(error_class, Exception)

    def test_all_errors_inherit_from_exception(self):
        """Test all errors inherit from Exception"""
        error_classes = [
            StorageServiceError,
            GraphDBError,
            VectorDBError,
            InvalidDataError,
            DatabaseConnectionError,
        ]

        for error_class in error_classes:
            assert issubclass(error_class, Exception)

    def test_error_instantiation_with_inheritance(self):
        """Test error instances work with inheritance"""
        graph_error = GraphDBError("Graph test")
        vector_error = VectorDBError("Vector test")
        data_error = InvalidDataError("Data test")
        connection_error = DatabaseConnectionError("Connection test")

        # All should be instances of StorageServiceError
        errors = [graph_error, vector_error, data_error, connection_error]
        for error in errors:
            assert isinstance(error, StorageServiceError)
            assert isinstance(error, Exception)

    def test_error_method_inheritance(self):
        """Test inherited methods work correctly"""
        graph_error = GraphDBError("Inheritance test", operation="test_op")

        # Should have inherited to_dict method
        result = graph_error.to_dict()

        assert "error_type" in result
        assert "message" in result
        assert "error_code" in result
        assert "details" in result
        assert result["error_type"] == "GraphDBError"


class TestErrorEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_message_error(self):
        """Test error with empty message"""
        error = StorageServiceError("")

        assert error.message == ""
        assert str(error) == ""

    def test_none_values_in_details(self):
        """Test errors handle None values in optional parameters"""
        # GraphDBError with None values
        graph_error = GraphDBError("Test", operation=None, node_type=None)
        assert "operation" not in graph_error.details
        assert "node_type" not in graph_error.details

        # VectorDBError with None values
        vector_error = VectorDBError("Test", collection_name=None, vector_size=None)
        assert "collection_name" not in vector_error.details
        assert "vector_size" not in vector_error.details

    def test_zero_values_in_details(self):
        """Test errors handle zero values correctly"""
        vector_error = VectorDBError("Test", vector_size=0)
        # Zero should not be added to details (falsy value)
        assert "vector_size" not in vector_error.details

    def test_error_with_complex_details(self):
        """Test error with complex details dictionary"""
        complex_details = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "bool": True,
            "none": None,
        }

        error = StorageServiceError("Complex test", details=complex_details)

        assert error.details == complex_details

        # to_dict should preserve complex structure
        result = error.to_dict()
        assert result["details"] == complex_details

    def test_error_string_representation(self):
        """Test error string representations"""
        errors = [
            StorageServiceError("Storage error"),
            GraphDBError("Graph error", operation="test"),
            VectorDBError("Vector error", collection_name="test"),
            InvalidDataError("Data error", data_type="test"),
            DatabaseConnectionError("Connection error", database_type="test"),
        ]

        for error in errors:
            error_str = str(error)
            assert len(error_str) > 0
            assert "error" in error_str.lower()

    def test_error_repr_method(self):
        """Test error repr method"""
        error = StorageServiceError("Repr test", error_code="R001")

        repr_str = repr(error)
        assert len(repr_str) > 0
        # Should be a valid representation
        assert "StorageServiceError" in repr_str

    def test_kwargs_handling_in_subclasses(self):
        """Test kwargs are properly passed to parent class"""
        # Test kwargs are passed through properly
        error = GraphDBError(
            "Kwargs test",
            operation="test",
            error_code="K001",
            details={"extra": "data"},
        )

        assert error.error_code == "K001"
        assert error.details["extra"] == "data"
        assert error.details["operation"] == "test"

    def test_multiple_error_creation(self):
        """Test creating multiple errors doesn't interfere"""
        error1 = GraphDBError("Error 1", operation="op1")
        error2 = VectorDBError("Error 2", collection_name="col2")
        error3 = InvalidDataError("Error 3", data_type="type3")

        # Each should maintain its own state
        assert error1.details["operation"] == "op1"
        assert error2.details["collection_name"] == "col2"
        assert error3.details["data_type"] == "type3"

        # Should not interfere with each other
        assert "collection_name" not in error1.details
        assert "operation" not in error2.details
        assert "operation" not in error3.details
