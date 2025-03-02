class StorageServiceError(Exception):
    """Base class for all storage service errors"""
    pass


class GraphDBError(StorageServiceError):
    """Error in graph database operations"""
    pass


class VectorDBError(StorageServiceError):
    """Error in vector database operations"""
    pass


class InvalidDataError(StorageServiceError):
    """Error when input data is invalid"""
    pass


class DatabaseConnectionError(StorageServiceError):
    """Error connecting to database"""
    pass
