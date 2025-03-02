class SearchServiceError(Exception):
    """Base class for all search service errors"""
    pass


class DatabaseError(SearchServiceError):
    """Error in database operations"""
    pass


class EmbeddingError(SearchServiceError):
    """Error in embedding generation"""
    pass


class InvalidQueryError(SearchServiceError):
    """Error for invalid search queries"""
    pass


class ConfigurationError(SearchServiceError):
    """Error in service configuration"""
    pass
