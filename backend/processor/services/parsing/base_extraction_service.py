import abc

from core.domain.extraction import ParsedDocument


class BaseExtractionService(abc.ABC):
    """
    TODO: is it useful tho? think about it;
    + .docx parser to be added sooner
    """

    @abc.abstractmethod
    async def parse_to_json(self) -> ParsedDocument:
        pass
