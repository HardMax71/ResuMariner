import abc


class BaseExtractionService(abc.ABC):
    @abc.abstractmethod
    def get_num_pages(self) -> int:
        """
        Return the total number of pages (or images) processed.
        """
        pass

    @abc.abstractmethod
    def parse_to_json(self) -> dict:
        """
        Parse the input (PDF or image) and return a JSON structure that contains:
            - metadata (e.g. total pages, file type, processed_at timestamp)
            - content pages with text and any associated links (if applicable)
        """
        pass
