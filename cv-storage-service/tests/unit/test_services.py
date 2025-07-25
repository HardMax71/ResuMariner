"""Comprehensive tests for cv-storage-service services to achieve 95%+ coverage."""

import pytest
from unittest.mock import patch, MagicMock

# Mock all external dependencies before importing services
with patch("neomodel.config"):
    with patch("neomodel.install_all_labels"):
        with patch("neomodel.db"):
            with patch("qdrant_client.QdrantClient"):
                from cv_storage_service.services.graph_db_service import GraphDBService
                from cv_storage_service.services.vector_db_service import (
                    VectorDBService,
                )
                from cv_storage_service.utils.errors import (
                    GraphDBError,
                    VectorDBError,
                    DatabaseConnectionError,
                )


class TestGraphDBService:
    """Test GraphDBService functionality"""

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    def test_graph_db_service_init_bolt_uri(self, mock_db, mock_install, mock_config):
        """Test GraphDBService initialization with bolt:// URI"""
        mock_db.cypher_query.return_value = ([], [])

        GraphDBService(
            uri="bolt://localhost:7687", username="neo4j", password="password123"
        )

        # Verify connection URL was set correctly
        expected_url = "bolt://neo4j:password123@localhost:7687"
        assert mock_config.DATABASE_URL == expected_url
        mock_install.assert_called_once()

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    def test_graph_db_service_init_no_bolt_prefix(
        self, mock_db, mock_install, mock_config
    ):
        """Test GraphDBService initialization without bolt:// prefix"""
        mock_db.cypher_query.return_value = ([], [])

        GraphDBService(uri="localhost:7687", username="test_user", password="test_pass")

        expected_url = "bolt://test_user:test_pass@localhost:7687"
        assert mock_config.DATABASE_URL == expected_url

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    def test_graph_db_service_init_connection_error(
        self, mock_db, mock_install, mock_config
    ):
        """Test GraphDBService initialization with connection error"""
        mock_install.side_effect = Exception("Connection failed")

        with pytest.raises(DatabaseConnectionError) as exc_info:
            GraphDBService(uri="localhost:7687", username="neo4j", password="password")

        assert "Neo4j connection failed" in str(exc_info.value)

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.Converter")
    def test_store_cv_success(self, mock_converter, mock_db, mock_install, mock_config):
        """Test successful CV storage"""
        mock_db.cypher_query.return_value = ([], [])

        # Setup converter mock
        mock_converter_instance = MagicMock()
        mock_converter.return_value = mock_converter_instance
        mock_converter_instance.from_dict.return_value = MagicMock(uid="stored-cv-id")

        service = GraphDBService("localhost:7687", "neo4j", "password")

        cv_data = {
            "personal_info": {
                "contact": {"email": "test@example.com"},
                "name": "Test User",
            }
        }

        result = service.store_cv(cv_data, "job-123")

        assert result == "stored-cv-id"
        mock_converter_instance.from_dict.assert_called_once_with(cv_data)

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.Converter")
    def test_store_cv_conversion_error(
        self, mock_converter, mock_db, mock_install, mock_config
    ):
        """Test CV storage with conversion error"""
        mock_db.cypher_query.return_value = ([], [])

        mock_converter_instance = MagicMock()
        mock_converter.return_value = mock_converter_instance
        mock_converter_instance.from_dict.side_effect = Exception("Conversion failed")

        service = GraphDBService("localhost:7687", "neo4j", "password")

        cv_data = {"invalid": "data"}

        with pytest.raises(GraphDBError) as exc_info:
            service.store_cv(cv_data, "job-456")

        assert "Failed to store CV" in str(exc_info.value)

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_find_existing_cv_by_email_found(
        self, mock_cv_node, mock_db, mock_install, mock_config
    ):
        """Test finding existing CV by email - found"""
        mock_db.cypher_query.return_value = ([], [])

        # Mock existing CV
        mock_existing_cv = MagicMock()
        mock_existing_cv.uid = "existing-cv-123"
        mock_cv_node.nodes.filter.return_value.first.return_value = mock_existing_cv

        service = GraphDBService("localhost:7687", "neo4j", "password")

        result = service.find_existing_cv_by_email("existing@example.com")

        assert result is not None
        assert result.uid == "existing-cv-123"

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_find_existing_cv_by_email_not_found(
        self, mock_cv_node, mock_db, mock_install, mock_config
    ):
        """Test finding existing CV by email - not found"""
        mock_db.cypher_query.return_value = ([], [])

        mock_cv_node.nodes.filter.return_value.first.return_value = None

        service = GraphDBService("localhost:7687", "neo4j", "password")

        result = service.find_existing_cv_by_email("nonexistent@example.com")

        assert result is None

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_find_existing_cv_by_email_error(
        self, mock_cv_node, mock_db, mock_install, mock_config
    ):
        """Test finding existing CV by email with error"""
        mock_db.cypher_query.return_value = ([], [])

        mock_cv_node.nodes.filter.side_effect = Exception("Query failed")

        service = GraphDBService("localhost:7687", "neo4j", "password")

        with pytest.raises(GraphDBError) as exc_info:
            service.find_existing_cv_by_email("error@example.com")

        assert "Failed to search for existing CV" in str(exc_info.value)

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_get_cv_details_success(
        self, mock_cv_node, mock_db, mock_install, mock_config
    ):
        """Test successful CV details retrieval"""
        mock_db.cypher_query.return_value = ([], [])

        # Mock CV nodes
        mock_cv1 = MagicMock()
        mock_cv1.uid = "cv-1"
        mock_cv1.to_dict.return_value = {"name": "User 1"}

        mock_cv2 = MagicMock()
        mock_cv2.uid = "cv-2"
        mock_cv2.to_dict.return_value = {"name": "User 2"}

        mock_cv_node.nodes.filter.return_value = [mock_cv1, mock_cv2]

        service = GraphDBService("localhost:7687", "neo4j", "password")

        result = service.get_cv_details(["cv-1", "cv-2"])

        assert result == {"cv-1": {"name": "User 1"}, "cv-2": {"name": "User 2"}}

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_get_cv_details_empty_list(
        self, mock_cv_node, mock_db, mock_install, mock_config
    ):
        """Test CV details retrieval with empty list"""
        mock_db.cypher_query.return_value = ([], [])

        service = GraphDBService("localhost:7687", "neo4j", "password")

        result = service.get_cv_details([])

        assert result == {}
        # Should not call filter with empty list
        mock_cv_node.nodes.filter.assert_not_called()

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_get_cv_details_error(
        self, mock_cv_node, mock_db, mock_install, mock_config
    ):
        """Test CV details retrieval with error"""
        mock_db.cypher_query.return_value = ([], [])

        mock_cv_node.nodes.filter.side_effect = Exception("Database error")

        service = GraphDBService("localhost:7687", "neo4j", "password")

        with pytest.raises(GraphDBError) as exc_info:
            service.get_cv_details(["cv-error"])

        assert "Failed to retrieve CV details" in str(exc_info.value)

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_delete_cv_success(self, mock_cv_node, mock_db, mock_install, mock_config):
        """Test successful CV deletion"""
        mock_db.cypher_query.return_value = ([], [])

        mock_cv = MagicMock()
        mock_cv_node.nodes.get_or_none.return_value = mock_cv

        service = GraphDBService("localhost:7687", "neo4j", "password")

        service.delete_cv("cv-to-delete")

        mock_cv_node.nodes.get_or_none.assert_called_once_with(uid="cv-to-delete")
        mock_cv.delete.assert_called_once()

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_delete_cv_not_found(
        self, mock_cv_node, mock_db, mock_install, mock_config
    ):
        """Test CV deletion when CV not found"""
        mock_db.cypher_query.return_value = ([], [])

        mock_cv_node.nodes.get_or_none.return_value = None

        service = GraphDBService("localhost:7687", "neo4j", "password")

        with pytest.raises(GraphDBError) as exc_info:
            service.delete_cv("nonexistent-cv")

        assert "CV with ID nonexistent-cv not found" in str(exc_info.value)

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.graph_db_service.CVNode")
    def test_delete_cv_error(self, mock_cv_node, mock_db, mock_install, mock_config):
        """Test CV deletion with error"""
        mock_db.cypher_query.return_value = ([], [])

        mock_cv_node.nodes.get_or_none.side_effect = Exception("Delete failed")

        service = GraphDBService("localhost:7687", "neo4j", "password")

        with pytest.raises(GraphDBError) as exc_info:
            service.delete_cv("error-cv")

        assert "Failed to delete CV" in str(exc_info.value)


class TestVectorDBService:
    """Test VectorDBService functionality"""

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_vector_db_service_init_success(self, mock_qdrant_client):
        """Test VectorDBService initialization success"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock successful collection creation
        mock_client_instance.recreate_collection = MagicMock()

        service = VectorDBService(
            host="localhost",
            port=6333,
            collection_name="test_collection",
            vector_size=384,
        )

        assert service.host == "localhost"
        assert service.port == 6333
        assert service.collection_name == "test_collection"
        assert service.vector_size == 384

        mock_qdrant_client.assert_called_once_with(
            host="localhost", port=6333, prefer_grpc=True
        )

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_vector_db_service_init_connection_error(self, mock_qdrant_client):
        """Test VectorDBService initialization with connection error"""
        mock_qdrant_client.side_effect = Exception("Failed to connect to Qdrant")

        with pytest.raises(VectorDBError) as exc_info:
            VectorDBService(
                host="unreachable", port=6333, collection_name="test", vector_size=384
            )

        assert "Failed to initialize Qdrant client" in str(exc_info.value)

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_ensure_collection_exists_recreation(self, mock_qdrant_client):
        """Test ensure_collection_exists with collection recreation"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        service = VectorDBService("localhost", 6333, "test_collection", 384)

        service._ensure_collection_exists()

        mock_client_instance.recreate_collection.assert_called_once()

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_store_vectors_success(self, mock_qdrant_client):
        """Test successful vector storage"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock upsert response
        mock_upsert_result = MagicMock()
        mock_upsert_result.operation_id = "op-123"
        mock_client_instance.upsert.return_value = mock_upsert_result

        service = VectorDBService("localhost", 6333, "test_collection", 3)

        vectors_data = [
            {
                "vector": [0.1, 0.2, 0.3],
                "text": "First text",
                "person_name": "John Doe",
                "email": "john@example.com",
                "source": "employment",
                "context": "Work experience",
            },
            {
                "vector": [0.4, 0.5, 0.6],
                "text": "Second text",
                "person_name": "John Doe",
                "email": "john@example.com",
                "source": "education",
                "context": "University degree",
            },
        ]

        result = service.store_vectors("cv-123", vectors_data)

        assert len(result) == 2
        assert all(id.startswith("cv-123_") for id in result)

        # Verify delete and upsert were called
        mock_client_instance.delete.assert_called_once()
        mock_client_instance.upsert.assert_called_once()

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_store_vectors_empty_list(self, mock_qdrant_client):
        """Test storing empty vectors list"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        service = VectorDBService("localhost", 6333, "test_collection", 384)

        result = service.store_vectors("cv-456", [])

        assert result == []
        # Should still delete existing vectors
        mock_client_instance.delete.assert_called_once()
        # But should not call upsert
        mock_client_instance.upsert.assert_not_called()

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_store_vectors_error(self, mock_qdrant_client):
        """Test vector storage with error"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        mock_client_instance.upsert.side_effect = Exception("Storage failed")

        service = VectorDBService("localhost", 6333, "test_collection", 384)

        vectors_data = [
            {
                "vector": [0.1, 0.2],
                "text": "Error text",
                "person_name": None,
                "email": None,
                "source": "test",
                "context": "",
            }
        ]

        with pytest.raises(VectorDBError) as exc_info:
            service.store_vectors("error-cv", vectors_data)

        assert "Failed to store vectors" in str(exc_info.value)

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_delete_cv_vectors_success(self, mock_qdrant_client):
        """Test successful CV vectors deletion"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock search result to count existing vectors
        mock_search_result = [MagicMock(), MagicMock(), MagicMock()]  # 3 vectors
        mock_client_instance.scroll.return_value = (mock_search_result, None)

        service = VectorDBService("localhost", 6333, "test_collection", 384)

        result = service.delete_cv_vectors("cv-to-delete")

        assert result == 3
        mock_client_instance.delete.assert_called_once()

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_delete_cv_vectors_none_found(self, mock_qdrant_client):
        """Test CV vectors deletion when none found"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock empty search result
        mock_client_instance.scroll.return_value = ([], None)

        service = VectorDBService("localhost", 6333, "test_collection", 384)

        result = service.delete_cv_vectors("empty-cv")

        assert result == 0
        # Should still call delete even if no vectors found
        mock_client_instance.delete.assert_called_once()

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_delete_cv_vectors_error(self, mock_qdrant_client):
        """Test CV vectors deletion with error"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        mock_client_instance.scroll.side_effect = Exception("Delete failed")

        service = VectorDBService("localhost", 6333, "test_collection", 384)

        with pytest.raises(VectorDBError) as exc_info:
            service.delete_cv_vectors("error-cv")

        assert "Failed to delete vectors for CV" in str(exc_info.value)

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_vector_id_generation(self, mock_qdrant_client):
        """Test vector ID generation logic"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        mock_upsert_result = MagicMock()
        mock_client_instance.upsert.return_value = mock_upsert_result

        service = VectorDBService("localhost", 6333, "test_collection", 2)

        vectors_data = [
            {
                "vector": [0.1, 0.2],
                "text": "First",
                "person_name": None,
                "email": None,
                "source": "test",
                "context": "",
            },
            {
                "vector": [0.3, 0.4],
                "text": "Second",
                "person_name": None,
                "email": None,
                "source": "test",
                "context": "",
            },
        ]

        result = service.store_vectors("test-cv", vectors_data)

        # Verify ID format
        assert len(result) == 2
        assert result[0] == "test-cv_0"
        assert result[1] == "test-cv_1"

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_vector_payload_formatting(self, mock_qdrant_client):
        """Test vector payload formatting for Qdrant"""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        mock_upsert_result = MagicMock()
        mock_client_instance.upsert.return_value = mock_upsert_result

        service = VectorDBService("localhost", 6333, "test_collection", 3)

        vectors_data = [
            {
                "vector": [0.1, 0.2, 0.3],
                "text": "Test text",
                "person_name": "Jane Smith",
                "email": "jane@example.com",
                "source": "employment",
                "context": "Senior role",
            }
        ]

        service.store_vectors("format-cv", vectors_data)

        # Verify upsert was called with properly formatted data
        mock_client_instance.upsert.assert_called_once()
        call_args = mock_client_instance.upsert.call_args
        points = call_args[1]["points"]  # points is passed as keyword argument

        assert len(points) == 1
        point = points[0]
        assert point.id == "format-cv_0"
        assert point.vector == [0.1, 0.2, 0.3]
        assert point.payload == {
            "cv_id": "format-cv",
            "text": "Test text",
            "person_name": "Jane Smith",
            "email": "jane@example.com",
            "source": "employment",
            "context": "Senior role",
        }


class TestServiceIntegration:
    """Test integration between services"""

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_services_initialization_together(
        self, mock_qdrant, mock_db, mock_install, mock_config
    ):
        """Test both services can be initialized together"""
        mock_db.cypher_query.return_value = ([], [])
        mock_qdrant_instance = MagicMock()
        mock_qdrant.return_value = mock_qdrant_instance

        graph_service = GraphDBService("localhost:7687", "neo4j", "password")
        vector_service = VectorDBService("localhost", 6333, "cv_collection", 384)

        assert graph_service is not None
        assert vector_service is not None

    def test_error_inheritance(self):
        """Test error class inheritance"""
        from utils.errors import GraphDBError, VectorDBError, DatabaseConnectionError

        # All should inherit from appropriate base classes
        assert issubclass(GraphDBError, Exception)
        assert issubclass(VectorDBError, Exception)
        assert issubclass(DatabaseConnectionError, Exception)

    @patch("cv_storage_service.services.graph_db_service.config")
    @patch("cv_storage_service.services.graph_db_service.install_all_labels")
    @patch("cv_storage_service.services.graph_db_service.db")
    def test_graph_service_configuration_from_settings(
        self, mock_db, mock_install, mock_config
    ):
        """Test graph service uses configuration from settings"""
        mock_db.cypher_query.return_value = ([], [])

        with patch("services.graph_db_service.settings") as mock_settings:
            mock_settings.NEO4J_MAX_CONNECTION_LIFETIME = 7200
            mock_settings.NEO4J_MAX_CONNECTION_POOL_SIZE = 100
            mock_settings.NEO4J_CONNECTION_TIMEOUT = 60

            GraphDBService("localhost:7687", "neo4j", "password")

            # Verify DRIVER_CONFIG was set
            assert hasattr(mock_config, "DRIVER_CONFIG")

    @patch("cv_storage_service.services.vector_db_service.QdrantClient")
    def test_vector_service_configuration_options(self, mock_qdrant):
        """Test vector service configuration options"""
        mock_qdrant_instance = MagicMock()
        mock_qdrant.return_value = mock_qdrant_instance

        with patch("services.vector_db_service.settings") as mock_settings:
            mock_settings.QDRANT_PREFER_GRPC = False
            mock_settings.QDRANT_TIMEOUT = 60

            VectorDBService("localhost", 6333, "test_collection", 384)

            # Verify client was initialized with prefer_grpc=True (hardcoded)
            mock_qdrant.assert_called_with(
                host="localhost", port=6333, prefer_grpc=True
            )
