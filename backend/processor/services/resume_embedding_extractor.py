import logging
from dataclasses import dataclass

from core.domain.processing import EmbeddingTextData
from core.domain.resume import EmbeddingVector, Resume

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEmbeddingData:
    texts: list[str]
    text_data_list: list[EmbeddingTextData]


class ResumeEmbeddingExtractor:
    def extract_for_embedding(self, resume: Resume) -> ExtractedEmbeddingData:
        text_data_list = self._extract_texts(resume)
        texts = [item.text for item in text_data_list]

        return ExtractedEmbeddingData(texts=texts, text_data_list=text_data_list)

    def create_vectors(
        self, embeddings: list[list[float]], extracted_data: ExtractedEmbeddingData
    ) -> list[EmbeddingVector]:
        vectors = [
            EmbeddingVector(
                vector=embedding,
                text=text_data.text,
                source=text_data.source,
                context=text_data.context,
            )
            for embedding, text_data in zip(embeddings, extracted_data.text_data_list, strict=False)
        ]
        return vectors

    def _extract_texts(self, resume: Resume) -> list[EmbeddingTextData]:
        results: list[EmbeddingTextData] = []

        if resume.professional_profile and resume.professional_profile.summary:
            results.append(EmbeddingTextData(resume.professional_profile.summary, "summary", None))

        results.extend(EmbeddingTextData(s.name, "skill", None) for s in resume.skills)

        for employment in resume.employment_history:
            results.extend(
                EmbeddingTextData(kp.text, "employment", employment.position) for kp in employment.key_points
            )

        for project in resume.projects:
            results.extend(EmbeddingTextData(kp.text, "project", project.title) for kp in (project.key_points or []))

        for edu in resume.education:
            inst = edu.institution.name
            context = f"{edu.qualification} at {inst}" if edu.qualification else inst
            results.extend(EmbeddingTextData(ex.text, "education", context) for ex in (edu.extras or []))

        return results
