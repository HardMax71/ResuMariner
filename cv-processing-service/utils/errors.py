class BaseProcessingError(Exception):
    """Base class for processing service errors"""
    pass


class ParserError(BaseProcessingError):
    """Error in document parsing"""
    pass


class LLMServiceError(BaseProcessingError):
    """Error in LLM service operations"""
    pass


class ContentStructureError(BaseProcessingError):
    """Error in content structuring"""
    pass


class DataFixerError(BaseProcessingError):
    """Error in data fixing"""
    pass


class ReviewServiceError(BaseProcessingError):
    """Error in review generation"""
    pass


class EmbeddingServiceError(BaseProcessingError):
    """Error in embedding generation"""
    pass
