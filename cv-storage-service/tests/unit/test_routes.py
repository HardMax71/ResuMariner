"""Comprehensive tests for cv-storage-service routes to achieve 95%+ coverage."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock all external dependencies before importing
with patch("neomodel.config"):
    with patch("neomodel.install_all_labels"):
        with patch("neomodel.db"):
            with patch("qdrant_client.QdrantClient"):
                with patch(
                    "cv_storage_service.services.graph_db_service.GraphDBService"
                ):
                    with patch(
                        "cv_storage_service.services.vector_db_service.VectorDBService"
                    ):
                        with patch.dict(
                            "os.environ",
                            {
                                "NEO4J_URI": "neo4j://localhost:7687",
                                "NEO4J_USERNAME": "neo4j",
                                "NEO4J_PASSWORD": "test_password",
                            },
                        ):
                            from cv_storage_service.utils.errors import (
                                GraphDBError,
                                VectorDBError,
                                StorageServiceError,
                            )


class TestStorageRoutes:
    """Test storage route functionality"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked database services"""
        with (
            patch("cv_storage_service.routes.storage_routes.graph_db") as mock_graph_db,
            patch(
                "cv_storage_service.routes.storage_routes.vector_db"
            ) as mock_vector_db,
        ):
            # Setup mock instances
            mock_graph_db.return_value = MagicMock()
            mock_vector_db.return_value = MagicMock()

            # Import after mocking to avoid initialization errors
            from cv_storage_service.routes.storage_routes import router
            from fastapi import FastAPI

            app = FastAPI()
            app.include_router(router)

            return TestClient(app)

    @pytest.fixture
    def valid_cv_data(self):
        """Create valid CV data for testing"""
        return {
            "personal_info": {
                "contact": {"email": "test@example.com", "phone": "+1234567890"},
                "name": "John Doe",
                "title": "Software Engineer",
            },
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Developer",
                    "duration": "2020-2023",
                }
            ],
            "education": [
                {
                    "institution": "University",
                    "degree": "Computer Science",
                    "year": "2020",
                }
            ],
        }

    @patch("routes.storage_routes.graph_db")
    def test_store_cv_success_new_cv(self, mock_graph_db, client, valid_cv_data):
        """Test successful CV storage for new CV"""
        # Setup mocks
        mock_graph_db.find_existing_cv_by_email.return_value = None
        mock_graph_db.store_cv.return_value = "graph-id-123"

        request_data = {"job_id": "job-123", "cv_data": valid_cv_data}

        response = client.post("/cv", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["graph_id"] == "graph-id-123"
        assert data["vector_count"] == 0

        # Verify service calls
        mock_graph_db.find_existing_cv_by_email.assert_called_once_with(
            "test@example.com"
        )
        mock_graph_db.store_cv.assert_called_once_with(valid_cv_data, "job-123")

    @patch("routes.storage_routes.graph_db")
    def test_store_cv_success_update_existing(
        self, mock_graph_db, client, valid_cv_data
    ):
        """Test successful CV storage for existing CV"""
        # Setup mocks - CV already exists
        mock_graph_db.find_existing_cv_by_email.return_value = {"id": "existing-id"}
        mock_graph_db.store_cv.return_value = "updated-graph-id-456"

        request_data = {"job_id": "job-456", "cv_data": valid_cv_data}

        response = client.post("/cv", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["graph_id"] == "updated-graph-id-456"
        assert data["vector_count"] == 0

    @patch("routes.storage_routes.graph_db")
    def test_store_cv_unknown_email(self, mock_graph_db, client):
        """Test CV storage with unknown email"""
        cv_data_no_email = {"personal_info": {"contact": {}, "name": "Anonymous User"}}

        mock_graph_db.store_cv.return_value = "anon-graph-id"

        request_data = {"job_id": "anon-job", "cv_data": cv_data_no_email}

        response = client.post("/cv", json=request_data)

        assert response.status_code == 200

        # Should not try to find existing CV with unknown email
        mock_graph_db.find_existing_cv_by_email.assert_not_called()

    @patch("routes.storage_routes.graph_db")
    def test_store_cv_graph_db_error(self, mock_graph_db, client, valid_cv_data):
        """Test CV storage with graph database error"""
        mock_graph_db.find_existing_cv_by_email.return_value = None
        mock_graph_db.store_cv.side_effect = GraphDBError("Graph DB connection failed")

        request_data = {"job_id": "error-job", "cv_data": valid_cv_data}

        response = client.post("/cv", json=request_data)

        assert response.status_code == 500
        data = response.json()
        assert "Graph database error" in data["detail"]
        assert "Graph DB connection failed" in data["detail"]

    @patch("routes.storage_routes.graph_db")
    def test_store_cv_unexpected_error(self, mock_graph_db, client, valid_cv_data):
        """Test CV storage with unexpected error"""
        mock_graph_db.find_existing_cv_by_email.side_effect = Exception(
            "Unexpected error"
        )

        request_data = {"job_id": "unexpected-job", "cv_data": valid_cv_data}

        response = client.post("/cv", json=request_data)

        assert response.status_code == 500
        data = response.json()
        assert "Storage operation failed" in data["detail"]
        assert "Unexpected error" in data["detail"]

    def test_store_cv_invalid_request_data(self, client):
        """Test CV storage with invalid request data"""
        invalid_request = {
            "job_id": "invalid-job"
            # Missing cv_data
        }

        response = client.post("/cv", json=invalid_request)

        assert response.status_code == 422  # Validation error

    @patch("routes.storage_routes.graph_db")
    def test_get_cv_success(self, mock_graph_db, client):
        """Test successful CV retrieval"""
        cv_details = {
            "cv-123": {
                "personal_info": {
                    "name": "Retrieved User",
                    "contact": {"email": "retrieved@example.com"},
                }
            }
        }
        mock_graph_db.get_cv_details.return_value = cv_details

        response = client.get("/cv/cv-123")

        assert response.status_code == 200
        data = response.json()
        assert data["personal_info"]["name"] == "Retrieved User"

        mock_graph_db.get_cv_details.assert_called_once_with(["cv-123"])

    @patch("routes.storage_routes.graph_db")
    def test_get_cv_not_found_empty_response(self, mock_graph_db, client):
        """Test CV retrieval with empty response"""
        mock_graph_db.get_cv_details.return_value = {}

        response = client.get("/cv/nonexistent-cv")

        assert response.status_code == 404
        data = response.json()
        assert "CV with ID nonexistent-cv not found" in data["detail"]

    @patch("routes.storage_routes.graph_db")
    def test_get_cv_not_found_none_response(self, mock_graph_db, client):
        """Test CV retrieval with None response"""
        mock_graph_db.get_cv_details.return_value = None

        response = client.get("/cv/none-cv")

        assert response.status_code == 404
        data = response.json()
        assert "CV with ID none-cv not found" in data["detail"]

    @patch("routes.storage_routes.graph_db")
    def test_get_cv_wrong_id_in_response(self, mock_graph_db, client):
        """Test CV retrieval with wrong ID in response"""
        cv_details = {"different-cv-id": {"personal_info": {"name": "Wrong User"}}}
        mock_graph_db.get_cv_details.return_value = cv_details

        response = client.get("/cv/requested-cv")

        assert response.status_code == 404
        data = response.json()
        assert "CV with ID requested-cv not found" in data["detail"]

    @patch("routes.storage_routes.graph_db")
    def test_get_cv_graph_db_error(self, mock_graph_db, client):
        """Test CV retrieval with graph database error"""
        mock_graph_db.get_cv_details.side_effect = GraphDBError("Failed to query graph")

        response = client.get("/cv/error-cv")

        assert response.status_code == 500
        data = response.json()
        assert "Graph database error" in data["detail"]
        assert "Failed to query graph" in data["detail"]

    @patch("routes.storage_routes.graph_db")
    def test_get_cv_unexpected_error(self, mock_graph_db, client):
        """Test CV retrieval with unexpected error"""
        mock_graph_db.get_cv_details.side_effect = Exception("Database timeout")

        response = client.get("/cv/timeout-cv")

        assert response.status_code == 500
        data = response.json()
        assert "Retrieval operation failed" in data["detail"]
        assert "Database timeout" in data["detail"]

    @patch("routes.storage_routes.vector_db")
    def test_store_vectors_success(self, mock_vector_db, client):
        """Test successful vector storage"""
        mock_vector_db.store_vectors.return_value = ["vec-1", "vec-2", "vec-3"]

        request_data = {
            "cv_id": "cv-123",
            "vectors": [
                {
                    "vector": [0.1, 0.2, 0.3],
                    "text": "First text",
                    "source": "employment",
                },
                {
                    "vector": [0.4, 0.5, 0.6],
                    "text": "Second text",
                    "person_name": "John Doe",
                    "email": "john@example.com",
                    "source": "education",
                    "context": "University degree",
                },
            ],
        }

        response = client.post("/vectors", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["vector_count"] == 3

        # Verify formatted vectors were passed correctly
        mock_vector_db.store_vectors.assert_called_once()
        call_args = mock_vector_db.store_vectors.call_args
        assert call_args[0][0] == "cv-123"  # cv_id
        formatted_vectors = call_args[0][1]
        assert len(formatted_vectors) == 2
        assert formatted_vectors[0]["vector"] == [0.1, 0.2, 0.3]
        assert formatted_vectors[1]["person_name"] == "John Doe"
        assert formatted_vectors[1]["context"] == "University degree"

    @patch("routes.storage_routes.vector_db")
    def test_store_vectors_empty_context(self, mock_vector_db, client):
        """Test vector storage with empty context"""
        mock_vector_db.store_vectors.return_value = ["vec-1"]

        request_data = {
            "cv_id": "cv-456",
            "vectors": [
                {"vector": [0.1, 0.2], "text": "Text without context", "source": "test"}
            ],
        }

        response = client.post("/vectors", json=request_data)

        assert response.status_code == 200

        # Verify context is converted to empty string
        call_args = mock_vector_db.store_vectors.call_args
        formatted_vectors = call_args[0][1]
        assert formatted_vectors[0]["context"] == ""

    @patch("routes.storage_routes.vector_db")
    def test_store_vectors_vector_db_error(self, mock_vector_db, client):
        """Test vector storage with vector database error"""
        mock_vector_db.store_vectors.side_effect = VectorDBError(
            "Vector DB connection failed"
        )

        request_data = {
            "cv_id": "error-cv",
            "vectors": [{"vector": [0.1], "text": "Error text", "source": "test"}],
        }

        response = client.post("/vectors", json=request_data)

        assert response.status_code == 500
        data = response.json()
        assert "Vector database error" in data["detail"]
        assert "Vector DB connection failed" in data["detail"]

    @patch("routes.storage_routes.vector_db")
    def test_store_vectors_unexpected_error(self, mock_vector_db, client):
        """Test vector storage with unexpected error"""
        mock_vector_db.store_vectors.side_effect = Exception("Memory error")

        request_data = {
            "cv_id": "memory-error-cv",
            "vectors": [
                {"vector": [0.1], "text": "Memory error text", "source": "test"}
            ],
        }

        response = client.post("/vectors", json=request_data)

        assert response.status_code == 500
        data = response.json()
        assert "Vector storage failed" in data["detail"]
        assert "Memory error" in data["detail"]

    def test_store_vectors_invalid_request(self, client):
        """Test vector storage with invalid request"""
        invalid_request = {
            "cv_id": "invalid-cv"
            # Missing vectors
        }

        response = client.post("/vectors", json=invalid_request)

        assert response.status_code == 422  # Validation error

    @patch("routes.storage_routes.graph_db")
    @patch("routes.storage_routes.vector_db")
    def test_delete_cv_success(self, mock_vector_db, mock_graph_db, client):
        """Test successful CV deletion"""
        mock_vector_db.delete_cv_vectors.return_value = 5

        response = client.delete("/cv/cv-123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "CV cv-123 deleted successfully" in data["message"]

        mock_graph_db.delete_cv.assert_called_once_with("cv-123")
        mock_vector_db.delete_cv_vectors.assert_called_once_with("cv-123")

    @patch("routes.storage_routes.graph_db")
    @patch("routes.storage_routes.vector_db")
    def test_delete_cv_storage_service_error(
        self, mock_vector_db, mock_graph_db, client
    ):
        """Test CV deletion with storage service error"""
        mock_graph_db.delete_cv.side_effect = StorageServiceError(
            "Failed to delete from graph"
        )

        response = client.delete("/cv/error-cv")

        assert response.status_code == 500
        data = response.json()
        assert "Failed to delete from graph" in data["detail"]

    @patch("routes.storage_routes.graph_db")
    def test_delete_cv_unexpected_error(self, mock_graph_db, client):
        """Test CV deletion with unexpected error"""
        mock_graph_db.delete_cv.side_effect = Exception("Disk full")

        response = client.delete("/cv/disk-error-cv")

        assert response.status_code == 500
        data = response.json()
        assert "Delete operation failed" in data["detail"]
        assert "Disk full" in data["detail"]

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "cv-storage-service"
        assert data["graph_db"] == "connected"
        assert data["vector_db"] == "connected"


class TestRouteInitialization:
    """Test route initialization and module-level setup"""

    @patch("routes.storage_routes.GraphDBService")
    @patch("routes.storage_routes.VectorDBService")
    def test_database_services_initialization_success(
        self, mock_vector_db, mock_graph_db
    ):
        """Test successful database services initialization"""
        # Mock successful initialization
        mock_graph_instance = MagicMock()
        mock_vector_instance = MagicMock()
        mock_graph_db.return_value = mock_graph_instance
        mock_vector_db.return_value = mock_vector_instance

        # Import module to trigger initialization
        import importlib
        import routes.storage_routes

        importlib.reload(routes.storage_routes)

        # Verify services were initialized
        mock_graph_db.assert_called()
        mock_vector_db.assert_called()

    @patch("routes.storage_routes.GraphDBService")
    @patch("routes.storage_routes.logger")
    def test_database_connection_error_initialization(self, mock_logger, mock_graph_db):
        """Test initialization with database connection error"""
        from utils.errors import DatabaseConnectionError

        mock_graph_db.side_effect = DatabaseConnectionError(
            "Failed to connect to Neo4j"
        )

        with pytest.raises(DatabaseConnectionError):
            import importlib
            import routes.storage_routes

            importlib.reload(routes.storage_routes)

        mock_logger.error.assert_called()

    @patch("routes.storage_routes.GraphDBService")
    @patch("routes.storage_routes.logger")
    def test_unexpected_error_initialization(self, mock_logger, mock_graph_db):
        """Test initialization with unexpected error"""
        mock_graph_db.side_effect = Exception("Unexpected init error")

        with pytest.raises(Exception):
            import importlib
            import routes.storage_routes

            importlib.reload(routes.storage_routes)

        mock_logger.error.assert_called()

    def test_router_instance_creation(self):
        """Test router instance is created correctly"""
        from routes.storage_routes import router
        from fastapi import APIRouter

        assert isinstance(router, APIRouter)

    def test_logging_configuration(self):
        """Test logging is configured"""
        from routes.storage_routes import logger
        import logging

        assert isinstance(logger, logging.Logger)
        assert logger.name == "routes.storage_routes"


class TestEndpointResponseModels:
    """Test endpoint response models and schemas"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked services"""
        with (
            patch("cv_storage_service.routes.storage_routes.graph_db") as mock_graph_db,
            patch(
                "cv_storage_service.routes.storage_routes.vector_db"
            ) as mock_vector_db,
        ):
            mock_graph_db.return_value = MagicMock()
            mock_vector_db.return_value = MagicMock()

            from cv_storage_service.routes.storage_routes import router
            from fastapi import FastAPI

            app = FastAPI()
            app.include_router(router)

            return TestClient(app)

    def test_store_cv_response_model(self, client):
        """Test store CV endpoint has correct response model"""
        from routes.storage_routes import router

        # Find the store CV route
        store_cv_route = None
        for route in router.routes:
            if (
                hasattr(route, "path")
                and route.path == "/cv"
                and hasattr(route, "methods")
                and "POST" in route.methods
            ):
                store_cv_route = route
                break

        assert store_cv_route is not None
        assert hasattr(store_cv_route, "response_model")

    def test_store_vectors_response_model(self, client):
        """Test store vectors endpoint has correct response model"""
        from routes.storage_routes import router

        # Find the store vectors route
        store_vectors_route = None
        for route in router.routes:
            if (
                hasattr(route, "path")
                and route.path == "/vectors"
                and hasattr(route, "methods")
                and "POST" in route.methods
            ):
                store_vectors_route = route
                break

        assert store_vectors_route is not None
        assert hasattr(store_vectors_route, "response_model")

    def test_all_endpoints_exist(self):
        """Test all expected endpoints exist in router"""
        from routes.storage_routes import router

        paths = []
        methods = []
        for route in router.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                paths.append(route.path)
                methods.extend(route.methods)

        assert "/cv" in paths
        assert "/cv/{cv_id}" in paths
        assert "/vectors" in paths
        assert "/health" in paths
        assert "POST" in methods
        assert "GET" in methods
        assert "DELETE" in methods


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked services"""
        with (
            patch("cv_storage_service.routes.storage_routes.graph_db") as mock_graph_db,
            patch(
                "cv_storage_service.routes.storage_routes.vector_db"
            ) as mock_vector_db,
        ):
            mock_graph_db.return_value = MagicMock()
            mock_vector_db.return_value = MagicMock()

            from cv_storage_service.routes.storage_routes import router
            from fastapi import FastAPI

            app = FastAPI()
            app.include_router(router)

            return TestClient(app)

    @patch("routes.storage_routes.vector_db")
    def test_store_vectors_empty_list(self, mock_vector_db, client):
        """Test storing empty vectors list"""
        mock_vector_db.store_vectors.return_value = []

        request_data = {"cv_id": "empty-cv", "vectors": []}

        response = client.post("/vectors", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["vector_count"] == 0

    @patch("routes.storage_routes.graph_db")
    def test_store_cv_missing_personal_info_sections(self, mock_graph_db, client):
        """Test CV storage with minimal personal_info"""
        cv_data = {"personal_info": {"contact": {"email": "minimal@example.com"}}}

        mock_graph_db.find_existing_cv_by_email.return_value = None
        mock_graph_db.store_cv.return_value = "minimal-id"

        request_data = {"job_id": "minimal-job", "cv_data": cv_data}

        response = client.post("/cv", json=request_data)

        assert response.status_code == 200

    @patch("routes.storage_routes.vector_db")
    def test_store_vectors_large_vector_count(self, mock_vector_db, client):
        """Test storing large number of vectors"""
        # Simulate storing 1000 vectors
        mock_vector_db.store_vectors.return_value = [f"vec-{i}" for i in range(1000)]

        vectors = [
            {"vector": [0.1] * 10, "text": f"Text {i}", "source": "test"}
            for i in range(10)  # Send 10, but service returns 1000 IDs
        ]

        request_data = {"cv_id": "large-cv", "vectors": vectors}

        response = client.post("/vectors", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["vector_count"] == 1000
