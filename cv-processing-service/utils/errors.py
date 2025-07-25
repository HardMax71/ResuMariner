class BaseProcessingError(Exception):
    """Base class for processing service errors"""

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


class ParserError(BaseProcessingError):
    """Error in document parsing"""

    def __init__(
        self, message: str, file_type: str = None, parser_type: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.file_type = file_type
        self.parser_type = parser_type
        if file_type:
            self.details["file_type"] = file_type
        if parser_type:
            self.details["parser_type"] = parser_type


class LLMServiceError(BaseProcessingError):
    """Error in LLM service operations"""

    def __init__(
        self, message: str, model_name: str = None, prompt_length: int = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.prompt_length = prompt_length
        if model_name:
            self.details["model_name"] = model_name
        if prompt_length:
            self.details["prompt_length"] = prompt_length


class ContentStructureError(BaseProcessingError):
    """Error in content structuring"""

    def __init__(
        self,
        message: str,
        content_type: str = None,
        validation_errors: list = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.content_type = content_type
        self.validation_errors = validation_errors or []
        if content_type:
            self.details["content_type"] = content_type
        if validation_errors:
            self.details["validation_errors"] = validation_errors


class DataFixerError(BaseProcessingError):
    """Error in data fixing"""

    def __init__(
        self, message: str, field_name: str = None, attempted_fix: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.attempted_fix = attempted_fix
        if field_name:
            self.details["field_name"] = field_name
        if attempted_fix:
            self.details["attempted_fix"] = attempted_fix


class ReviewServiceError(BaseProcessingError):
    """Error in review generation"""

    def __init__(
        self,
        message: str,
        review_type: str = None,
        content_length: int = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.review_type = review_type
        self.content_length = content_length
        if review_type:
            self.details["review_type"] = review_type
        if content_length:
            self.details["content_length"] = content_length


class EmbeddingServiceError(BaseProcessingError):
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
