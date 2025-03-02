import logging
from typing import List, Dict, Any

import httpx
from config import settings
from models.resume_models import ResumeStructure
from sentence_transformers import SentenceTransformer
from utils.errors import EmbeddingServiceError


class EmbeddingService:
    """Service for generating embeddings from CV text data and sending to storage"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding service with the specified model"""
        try:
            self.model = SentenceTransformer(model_name)
            self.storage_url = settings.STORAGE_SERVICE_URL
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to initialize embedding service: {str(e)}")

    def _create_embedding(self, text: str, source: str, context: str, metadata: Dict[str, Any]) -> Dict[
                                                                                                       str, Any] | None:
        """Helper method to create a single embedding with metadata"""
        if not text:
            return None

        vector = self.model.encode(text).tolist()
        return {
            "vector": vector,
            "text": text,
            "source": source,
            "context": context,
            **metadata
        }

    def _process_list_items(self, items: List, field_name: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a list of items for embedding generation"""
        embeddings = []
        if not items:
            return embeddings

        # Process list as a single text entry
        combined_text = ", ".join([str(item) for item in items if item])
        if combined_text:
            embedding = self._create_embedding(
                text=combined_text,
                source=field_name,
                context=f"{field_name.capitalize()} list",
                metadata=metadata
            )
            if embedding:
                embeddings.append(embedding)

        return embeddings

    def generate_embeddings(self, resume: ResumeStructure) -> List[Dict[str, Any]]:
        """Generate embeddings for all searchable content in the CV"""
        try:
            embeddings = []

            # Extract core metadata fields
            name = resume.personal_info.name
            email = resume.personal_info.contact.email
            base_metadata = {"person_name": name, "email": email}

            # 1. Personal Information
            # Name
            name_embedding = self._create_embedding(
                text=name,
                source="personal_info",
                context="Name",
                metadata=base_metadata
            )
            if name_embedding:
                embeddings.append(name_embedding)

            # Email
            email_embedding = self._create_embedding(
                text=email,
                source="personal_info",
                context="Email",
                metadata=base_metadata
            )
            if email_embedding:
                embeddings.append(email_embedding)

            # Location
            if resume.personal_info.demographics.current_location:
                location = resume.personal_info.demographics.current_location
                location_parts = []
                if location.city:
                    location_parts.append(location.city)
                if location.state:
                    location_parts.append(location.state)
                if location.country:
                    location_parts.append(location.country)

                location_text = ", ".join(location_parts)
                if location_text:
                    embeddings.append(self._create_embedding(
                        text=location_text,
                        source="personal_info",
                        context="Location",
                        metadata=base_metadata
                    ))

            # 2. Professional Profile
            if resume.professional_profile:
                # Summary
                if resume.professional_profile.summary:
                    embeddings.append(self._create_embedding(
                        text=resume.professional_profile.summary,
                        source="professional_profile",
                        context="Summary",
                        metadata=base_metadata
                    ))

                # Role
                if resume.professional_profile.preferences.role:
                    embeddings.append(self._create_embedding(
                        text=resume.professional_profile.preferences.role,
                        source="professional_profile",
                        context="Desired Role",
                        metadata=base_metadata
                    ))

            # 3. Skills (as a single combined vector)
            embeddings.extend(self._process_list_items(
                resume.skills,
                "skills",
                base_metadata
            ))

            # 4. Employment History
            for job in resume.employment_history:
                job_metadata = {
                    **base_metadata,
                    "company": job.company,
                    "position": job.position
                }

                # Position and company
                position_embedding = self._create_embedding(
                    text=f"{job.position} at {job.company}",
                    source="employment",
                    context="Job Title",
                    metadata=job_metadata
                )
                if position_embedding:
                    embeddings.append(position_embedding)

                # Key points
                for point in job.key_points:
                    embedding = self._create_embedding(
                        text=point,
                        source="employment",
                        context=f"{job.position} at {job.company}",
                        metadata=job_metadata
                    )
                    if embedding:
                        embeddings.append(embedding)

                # Tech stack
                embeddings.extend(self._process_list_items(
                    job.tech_stack,
                    "tech_stack",
                    job_metadata
                ))

            # 5. Projects
            if resume.projects:
                for project in resume.projects:
                    project_metadata = {
                        **base_metadata,
                        "project_title": project.title
                    }

                    # Project title
                    title_embedding = self._create_embedding(
                        text=project.title,
                        source="project",
                        context="Project Title",
                        metadata=project_metadata
                    )
                    if title_embedding:
                        embeddings.append(title_embedding)

                    # Key points
                    for point in project.key_points:
                        embedding = self._create_embedding(
                            text=point,
                            source="project",
                            context=project.title,
                            metadata=project_metadata
                        )
                        if embedding:
                            embeddings.append(embedding)

                    # Tech stack
                    embeddings.extend(self._process_list_items(
                        project.tech_stack,
                        "tech_stack",
                        project_metadata
                    ))

            # 6. Education
            if resume.education:
                for edu in resume.education:
                    edu_metadata = {
                        **base_metadata,
                        "institution": edu.institution,
                        "qualification": edu.qualification,
                        "field": edu.study_field
                    }

                    # Education summary
                    edu_text = f"{edu.qualification} in {edu.study_field} at {edu.institution}"
                    edu_embedding = self._create_embedding(
                        text=edu_text,
                        source="education",
                        context="Education",
                        metadata=edu_metadata
                    )
                    if edu_embedding:
                        embeddings.append(edu_embedding)

                    # Coursework
                    if edu.coursework:
                        embeddings.extend(self._process_list_items(
                            edu.coursework,
                            "coursework",
                            edu_metadata
                        ))

                    # Extras
                    if edu.extras:
                        embeddings.extend(self._process_list_items(
                            edu.extras,
                            "education_extras",
                            edu_metadata
                        ))

            # 7. Courses
            if resume.courses:
                for course in resume.courses:
                    course_metadata = {
                        **base_metadata,
                        "course_name": course.name,
                        "organization": course.organization
                    }

                    course_text = f"{course.name} by {course.organization}"
                    if course.year:
                        course_text += f" ({course.year})"

                    course_embedding = self._create_embedding(
                        text=course_text,
                        source="course",
                        context="Course",
                        metadata=course_metadata
                    )
                    if course_embedding:
                        embeddings.append(course_embedding)

            # 8. Certifications
            if resume.certifications:
                for cert in resume.certifications:
                    cert_metadata = {
                        **base_metadata,
                        "certification_name": cert.name,
                        "issuer": cert.issue_org
                    }

                    cert_text = cert.name
                    if cert.issue_org:
                        cert_text += f" by {cert.issue_org}"
                    if cert.issue_year:
                        cert_text += f" ({cert.issue_year})"

                    cert_embedding = self._create_embedding(
                        text=cert_text,
                        source="certification",
                        context="Certification",
                        metadata=cert_metadata
                    )
                    if cert_embedding:
                        embeddings.append(cert_embedding)

            # 9. Language Proficiency
            if resume.language_proficiency:
                for lang in resume.language_proficiency:
                    lang_metadata = {
                        **base_metadata,
                        "language": lang.language,
                        "level": lang.level.cefr
                    }

                    lang_text = f"{lang.language} ({lang.level.cefr})"
                    lang_embedding = self._create_embedding(
                        text=lang_text,
                        source="language",
                        context="Language Proficiency",
                        metadata=lang_metadata
                    )
                    if lang_embedding:
                        embeddings.append(lang_embedding)

            # 10. Awards
            if resume.awards:
                for award in resume.awards:
                    award_metadata = {
                        **base_metadata,
                        "award_name": award.name,
                        "organization": award.organization,
                        "position": award.position
                    }

                    award_text = f"{award.name} - {award.position} from {award.organization}"
                    if award.year:
                        award_text += f" ({award.year})"

                    award_embedding = self._create_embedding(
                        text=award_text,
                        source="award",
                        context="Award",
                        metadata=award_metadata
                    )
                    if award_embedding:
                        embeddings.append(award_embedding)

                    # Award description
                    if award.description:
                        desc_embedding = self._create_embedding(
                            text=award.description,
                            source="award",
                            context=award.name,
                            metadata=award_metadata
                        )
                        if desc_embedding:
                            embeddings.append(desc_embedding)

            # 11. Scientific Contributions
            if resume.scientific_contributions:
                contributions = resume.scientific_contributions
                if not isinstance(contributions, list):
                    contributions = [contributions]

                for contrib in contributions:
                    contrib_metadata = {
                        **base_metadata,
                        "title": contrib.title,
                        "publication_type": contrib.publication_type
                    }

                    # Title
                    title_embedding = self._create_embedding(
                        text=contrib.title,
                        source="publication",
                        context="Publication Title",
                        metadata=contrib_metadata
                    )
                    if title_embedding:
                        embeddings.append(title_embedding)

                    # Description
                    if contrib.description:
                        desc_embedding = self._create_embedding(
                            text=contrib.description,
                            source="publication",
                            context=contrib.title,
                            metadata=contrib_metadata
                        )
                        if desc_embedding:
                            embeddings.append(desc_embedding)

            # Log embedding count
            self.logger.info(f"Generated {len(embeddings)} embeddings for CV")
            return embeddings

        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise EmbeddingServiceError(f"Failed to generate embeddings: {str(e)}")

    async def send_embeddings_to_storage(self, cv_id: str, resume: ResumeStructure) -> bool:
        """Generate embeddings and send to storage service"""
        try:
            # Generate embeddings
            embeddings = self.generate_embeddings(resume)

            if not embeddings:
                self.logger.warning(f"No embeddings generated for CV {cv_id}")
                return False

            # Send embeddings to storage service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.storage_url}/vectors",
                    json={
                        "cv_id": cv_id,
                        "vectors": embeddings
                    },
                    timeout=60.0
                )

                if response.status_code != 200:
                    self.logger.error(f"Failed to store embeddings: {response.text}")
                    return False

                self.logger.info(f"Successfully stored {len(embeddings)} embeddings for CV {cv_id}")
                return True

        except Exception as e:
            self.logger.error(f"Error sending embeddings to storage: {str(e)}")
            return False
