from dataclasses import dataclass, field
from typing import NamedTuple

from core.domain.resume import Resume
from core.domain.review import ReviewResult


@dataclass
class ProcessingMetadata:
    filename: str = ""
    file_ext: str = ""
    source: str = ""
    page_count: int = 0
    graph_id: str | None = None
    graph_operation: str | None = None
    previous_graph_id: str | None = None
    embeddings_stored: bool = False
    embeddings_count: int = 0
    storage_error: str | None = None
    review_generated: bool = False
    review_error: str | None = None


@dataclass
class ProcessingResult:
    resume: Resume
    review: ReviewResult | None = None
    metadata: ProcessingMetadata = field(default_factory=ProcessingMetadata)


class EmbeddingTextData(NamedTuple):
    text: str
    source: str
    context: str | None = None
