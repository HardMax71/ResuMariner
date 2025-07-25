class StorageServiceError(Exception):
    """Base class for all storage service errors"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convert error to dictionary for JSON serialization"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class GraphDBError(StorageServiceError):
    """Error in graph database operations"""

    def __init__(
        self, message: str, operation: str = None, node_type: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.node_type = node_type
        if operation:
            self.details["operation"] = operation
        if node_type:
            self.details["node_type"] = node_type


class VectorDBError(StorageServiceError):
    """Error in vector database operations"""

    def __init__(
        self,
        message: str,
        collection_name: str = None,
        vector_size: int = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.collection_name = collection_name
        self.vector_size = vector_size
        if collection_name:
            self.details["collection_name"] = collection_name
        if vector_size:
            self.details["vector_size"] = vector_size


class InvalidDataError(StorageServiceError):
    """Error when input data is invalid"""

    def __init__(
        self,
        message: str,
        data_type: str = None,
        validation_errors: list = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.data_type = data_type
        self.validation_errors = validation_errors or []
        if data_type:
            self.details["data_type"] = data_type
        if validation_errors:
            self.details["validation_errors"] = validation_errors


class DatabaseConnectionError(StorageServiceError):
    """Error connecting to database"""

    def __init__(
        self,
        message: str,
        database_type: str = None,
        connection_string: str = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.database_type = database_type
        self.connection_string = connection_string
        if database_type:
            self.details["database_type"] = database_type
        if connection_string:
            # Don't log the full connection string for security
            self.details["connection_string"] = "[REDACTED]"
