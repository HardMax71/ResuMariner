class SearchServiceError(Exception):
    """Base class for all search service errors"""

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


class DatabaseError(SearchServiceError):
    """Error in database operations"""

    def __init__(
        self, message: str, database_type: str = None, operation: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.database_type = database_type
        self.operation = operation
        if database_type:
            self.details["database_type"] = database_type
        if operation:
            self.details["operation"] = operation


class EmbeddingError(SearchServiceError):
    """Error in embedding generation"""

    def __init__(
        self, message: str, model_name: str = None, text_length: int = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.text_length = text_length
        if model_name:
            self.details["model_name"] = model_name
        if text_length:
            self.details["text_length"] = text_length


class InvalidQueryError(SearchServiceError):
    """Error for invalid search queries"""

    def __init__(
        self,
        message: str,
        query_type: str = None,
        validation_errors: list = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.query_type = query_type
        self.validation_errors = validation_errors or []
        if query_type:
            self.details["query_type"] = query_type
        if validation_errors:
            self.details["validation_errors"] = validation_errors


class ConfigurationError(SearchServiceError):
    """Error in service configuration"""

    def __init__(
        self, message: str, config_key: str = None, expected_type: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.expected_type = expected_type
        if config_key:
            self.details["config_key"] = config_key
        if expected_type:
            self.details["expected_type"] = expected_type
