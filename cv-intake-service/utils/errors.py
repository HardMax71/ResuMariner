class BaseServiceError(Exception):
    """Base class for service errors"""
    pass


class RepositoryError(BaseServiceError):
    """Error in repository operations"""
    pass


class FileServiceError(BaseServiceError):
    """Error in file service operations"""
    pass


class ProcessingServiceError(BaseServiceError):
    """Error in processing service operations"""
    pass


class JobServiceError(BaseServiceError):
    """Error in job service operations"""
    pass
