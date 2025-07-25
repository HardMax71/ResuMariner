class BaseServiceError(Exception):
    """Base class for service errors"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    @property
    def code(self) -> str | None:
        """Backward compatibility property for error_code"""
        return self.error_code

    def to_dict(self) -> dict:
        """Convert error to dictionary for JSON serialization"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "code": self.error_code,
            "details": self.details,
        }


class RepositoryError(BaseServiceError):
    """Error in repository operations"""

    def __init__(
        self, message: str, operation: str = None, entity: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.entity = entity
        if operation:
            self.details["operation"] = operation
        if entity:
            self.details["entity"] = entity


class FileServiceError(BaseServiceError):
    """Error in file service operations"""

    def __init__(
        self, message: str, file_path: str = None, file_size: int = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.file_size = file_size
        if file_path:
            self.details["file_path"] = file_path
        if file_size:
            self.details["file_size"] = file_size


class ProcessingServiceError(BaseServiceError):
    """Error in processing service operations"""

    def __init__(
        self, message: str, status_code: int = None, response_text: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_text = response_text
        if status_code:
            self.details["status_code"] = status_code
        if response_text:
            self.details["response_text"] = response_text


class JobServiceError(BaseServiceError):
    """Error in job service operations"""

    def __init__(
        self, message: str, job_id: str = None, job_status: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.job_id = job_id
        self.job_status = job_status
        if job_id:
            self.details["job_id"] = job_id
        if job_status:
            self.details["job_status"] = job_status
