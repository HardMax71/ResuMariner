import argparse
import json
import os
import sys
import time

import requests
from tqdm import tqdm

# Import domain types from backend
from core.domain import ProcessingMetadata, Resume, ReviewResult


class CVProcessingTest:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        """Initialize with backend URL"""
        # Ensure no trailing slash for clean URL joins
        self.backend_url = backend_url.rstrip("/")
        self.cv_id: str | None = None  # Graph/Resume ID when available
        self.resume: Resume | None = None  # Properly typed Resume object
        self.review: ReviewResult | None = None  # Properly typed Review object
        self.metadata: ProcessingMetadata | None = None
        self.search_results: dict = {}

    def process_file(self, file_path: str) -> dict:
        print(f"Processing file: {file_path}")
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found")
            sys.exit(1)

        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        print("\n1. Uploading file...")
        try:
            with open(file_path, "rb") as file:
                files = {"file": (file_name, file, self._get_mime_type(file_ext))}
                # Backend now ignores client-provided toggles and uses settings; only send file
                print(f"Sending to: {self.backend_url}/api/v1/upload/")
                response = requests.post(
                    f"{self.backend_url}/api/v1/upload/",
                    files=files,
                    timeout=180,  # 3-minute timeout for processing
                )

                if response.status_code not in (200, 202):
                    print(f"Upload failed with status {response.status_code}: {response.text}")
                    sys.exit(1)

                upload_result = response.json()
                job_id = upload_result.get("job_id")

                if not job_id:
                    print("Error: No job ID returned from upload")
                    sys.exit(1)

                print(f"Upload accepted. Job ID: {job_id}")

            # Poll for processing completion
            print("\nWaiting for processing to complete...")
            max_retries = 120
            retry_interval = 2  # seconds

            for _ in tqdm(range(max_retries)):
                response = requests.get(f"{self.backend_url}/api/v1/jobs/{job_id}/", timeout=10)

                if response.status_code != 200:
                    print(f"Status check failed: {response.status_code} - {response.text}")
                    time.sleep(retry_interval)
                    continue

                status = response.json()
                if status.get("status") == "completed":
                    print("\nJob completed! Fetching results...")

                    result_response = requests.get(status["result_url"], timeout=120)
                    print(f"Fetching result from: {status['result_url']}")
                    result_data = result_response.json()

                    # Parse metadata
                    metadata_dict = result_data.get("metadata", {})
                    if metadata_dict:
                        self.metadata = ProcessingMetadata(**metadata_dict)
                        self.cv_id = self.metadata.graph_id or job_id
                    else:
                        self.cv_id = job_id

                    # Parse resume using Pydantic model
                    resume_data = result_data.get("resume")
                    if resume_data:
                        self.resume = Resume(**resume_data)

                    # Parse review using Pydantic model
                    review_data = result_data.get("review")
                    if review_data:
                        self.review = ReviewResult(**review_data)

                    print(f"Processing completed! CV ID: {self.cv_id}")
                    break  # EXIT THE LOOP IMMEDIATELY!
                elif status.get("status") == "failed":
                    print(f"Processing failed: {status.get('message')}")
                    sys.exit(1)

                time.sleep(retry_interval)
            else:
                # This else clause only runs if the loop completes without breaking
                print("Error: Processing timed out")
                sys.exit(1)

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            sys.exit(1)

    def extract_search_parameters(self) -> dict:
        """Extract various search parameters from the parsed resume data using typed access."""
        if not self.resume:
            return {}

        params = {}

        # Extract name - always present in PersonalInfo
        params["name"] = self.resume.personal_info.name

        # Extract email if available
        if self.resume.personal_info.contact and self.resume.personal_info.contact.email:
            params["email"] = self.resume.personal_info.contact.email

        # Extract skills - now properly typed Skill objects
        if self.resume.skills:
            skill_names = [skill.name for skill in self.resume.skills]
            params["all_skills"] = skill_names
            params["top_skills"] = skill_names[:3]

        # Extract role from professional_profile.preferences
        if (
            self.resume.professional_profile
            and self.resume.professional_profile.preferences
            and self.resume.professional_profile.preferences.role
        ):
            params["role"] = self.resume.professional_profile.preferences.role

        # Extract location from demographics
        if self.resume.personal_info.demographics:
            location = self.resume.personal_info.demographics.current_location
            if location:
                location_parts = []
                if location.city:
                    params["city"] = location.city
                    location_parts.append(location.city)
                if location.country:
                    params["country"] = location.country
                    location_parts.append(location.country)
                if location_parts:
                    params["location"] = ", ".join(location_parts)

        # Extract companies from employment history
        if self.resume.employment_history:
            companies = [emp.company.name for emp in self.resume.employment_history if emp.company]
            if companies:
                params["companies"] = companies
                params["latest_company"] = companies[0]  # Assuming most recent is first

        # Extract technologies from employment and projects
        all_technologies = set()

        # From employment history
        for emp in self.resume.employment_history:
            all_technologies.update(tech.name for tech in emp.technologies)

        # From projects
        for project in self.resume.projects:
            all_technologies.update(tech.name for tech in project.technologies)

        if all_technologies:
            tech_list = list(all_technologies)
            params["technologies"] = tech_list
            params["top_technologies"] = tech_list[:3]

        # Calculate years of experience from employment_history
        if self.resume.employment_history:
            total_months = sum(emp.duration.duration_months for emp in self.resume.employment_history if emp.duration)
            params["years_experience"] = total_months // 12

        return params

    def search_semantic(self, query: str, limit: int = 5, min_score: float = 0.0, filters: dict | None = None):
        """Perform semantic search against monolith search API."""
        try:
            search_payload = {"query": query, "limit": limit, "min_score": min_score}
            if filters:
                search_payload["filters"] = filters

            print(f"Sending to: {self.backend_url}/search/semantic/")
            print(f"Payload: {json.dumps(search_payload, indent=2, ensure_ascii=False)}")
            response = requests.post(f"{self.backend_url}/search/semantic/", json=search_payload, timeout=30)
            if response.status_code != 200:
                print(f"Semantic search failed: {response.status_code} - {response.text}")
                return None

            search_results = response.json()
            results = search_results.get("results", [])
            if not results:
                print("No results found")
                return None

            print(f"Found {len(results)} results (semantic search):")
            return results

        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return None

    def search_structured(
        self,
        skills: list | None = None,
        technologies: list | None = None,
        role: str | None = None,
        company: str | None = None,
        location: str | None = None,
        years_experience: int | None = None,
        limit: int = 5,
    ):
        """Perform structured search (graph search) using filters object."""
        try:
            filters_payload = {}
            if skills:
                filters_payload["skills"] = skills if isinstance(skills, list) else [skills]
            if technologies:
                filters_payload["technologies"] = technologies if isinstance(technologies, list) else [technologies]
            if role:
                filters_payload["role"] = role
            if company:
                filters_payload["company"] = company
            if location:
                filters_payload["location"] = location
            if years_experience is not None:
                filters_payload["years_experience"] = years_experience

            search_payload = {"limit": limit}
            if filters_payload:
                search_payload["filters"] = filters_payload

            print(f"Sending to: {self.backend_url}/search/structured/")
            print(f"Payload: {json.dumps(search_payload, indent=2, ensure_ascii=False)}")
            response = requests.post(f"{self.backend_url}/search/structured/", json=search_payload, timeout=30)
            if response.status_code != 200:
                print(f"Structured search failed: {response.status_code} - {response.text}")
                return None

            search_results = response.json()
            results = search_results.get("results", [])
            if not results:
                print("No results found")
                return None

            print(f"Found {len(results)} results (structured search):")
            return results

        except Exception as e:
            print(f"Error in structured search: {str(e)}")
            return None

    def search_hybrid(
        self,
        query: str,
        skills: list | None = None,
        technologies: list | None = None,
        role: str | None = None,
        company: str | None = None,
        location: str | None = None,
        vector_weight: float = 0.7,
        graph_weight: float = 0.3,
        limit: int = 5,
    ):
        """Perform hybrid search combining semantic and structured approaches."""
        try:
            search_payload = {
                "query": query,
                "limit": limit,
                "vector_weight": vector_weight,
                "graph_weight": graph_weight,
            }

            filters_payload = {}
            if skills:
                filters_payload["skills"] = skills if isinstance(skills, list) else [skills]
            if technologies:
                filters_payload["technologies"] = technologies if isinstance(technologies, list) else [technologies]
            if role:
                filters_payload["role"] = role
            if company:
                filters_payload["company"] = company
            if location:
                filters_payload["location"] = location

            if filters_payload:
                search_payload["filters"] = filters_payload

            print(f"Sending to: {self.backend_url}/search/hybrid/")
            print(f"Payload: {json.dumps(search_payload, indent=2, ensure_ascii=False)}")
            response = requests.post(f"{self.backend_url}/search/hybrid/", json=search_payload, timeout=30)
            if response.status_code != 200:
                print(f"Hybrid search failed: {response.status_code} - {response.text}")
                return None

            search_results = response.json()
            results = search_results.get("results", [])
            if not results:
                print("No results found")
                return None

            print(f"Found {len(results)} results (hybrid search):")
            return results

        except Exception as e:
            print(f"Error in hybrid search: {str(e)}")
            return None

    def get_filter_options(self):
        """Get available filter options for search"""
        try:
            print(f"Retrieving filter options from: {self.backend_url}/filters/")
            response = requests.get(f"{self.backend_url}/filters/", timeout=30)
            if response.status_code != 200:
                print(f"Failed to get filter options: {response.status_code} - {response.text}")
                return None
            filter_options = response.json()
            return filter_options

        except Exception as e:
            print(f"Error getting filter options: {str(e)}")
            return None

    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type for file extension"""
        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        return mime_types.get(extension, "application/octet-stream")

    def print_cv_summary(self):
        """Print a summary of the CV using the typed Resume object"""
        if not self.resume:
            print("No CV data available")
            return
        print("\n2. CV Summary:")
        print("=" * 80)
        # Use Pydantic's model_dump for clean JSON output
        print(json.dumps(self.resume.model_dump(exclude_none=True), indent=2, default=str, ensure_ascii=False))
        print("=" * 80)

    def print_review(self):
        """Print the review of the CV using the typed ReviewResult object"""
        if not self.review:
            print("No review data available")
            return
        print("\nCV Review:")
        print("=" * 80)
        # Use Pydantic's model_dump for clean JSON output
        print(json.dumps(self.review.model_dump(exclude_none=True), indent=2, default=str, ensure_ascii=False))
        print("=" * 80)

    def print_search_results(
        self, results: list, search_type: str = "", search_params: str = "", include_matches: bool = False
    ):
        """Print search results with optional match details"""
        if not results:
            return
        print(f"\nSearch Results ({search_type}):")
        if search_params:
            print(f"Parameters: {search_params}")
        print("=" * 80)
        # Prefer raw output of each result for clarity/debuggability
        for idx, result in enumerate(results):
            # Normalize legacy key and ensure name displays correctly
            if "person_name" in result and "name" not in result:
                result["name"] = result.get("person_name")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if idx < len(results) - 1:
                print("-" * 40)
        print("=" * 80)

    def run_comprehensive_search(self, include_matches: bool = False) -> dict:
        """Run a comprehensive set of searches using all available parameters from the CV"""
        if not self.resume:
            print("No CV data available for searching")
            return {}
        print("\n3. Running comprehensive search testing")
        params = self.extract_search_parameters()
        print("\nExtracted search parameters:")
        print(json.dumps(params, indent=2, ensure_ascii=False))
        search_results = {}

        # Run semantic searches
        semantic_categories = {
            "name": "Semantic search by name",
            "role": "Semantic search by role",
            "latest_company": "Semantic search by company",
            "location": "Semantic search by location",
            "top_skills": "Semantic search by skills",
        }
        for key, description in semantic_categories.items():
            if key in params:
                query = params[key]
                if isinstance(query, list):
                    query = ", ".join(query)
                print(f"\nRunning {description}: {query}")
                results = self.search_semantic(query)
                if results:
                    search_results[f"semantic_{key}"] = results
                    self.print_search_results(
                        results,
                        search_type=description,
                        search_params=query,
                        include_matches=include_matches,
                    )

        # Run structured searches
        structured_combinations = [
            {"skills": "top_skills", "description": "Structured search by top skills"},
            {"role": "role", "description": "Structured search by role"},
            {
                "company": "latest_company",
                "description": "Structured search by company",
            },
            {
                "skills": "top_skills",
                "role": "role",
                "description": "Structured search by skills and role",
            },
            {
                "technologies": "top_technologies",
                "description": "Structured search by technologies",
            },
        ]
        for combo in structured_combinations:
            description = combo.pop("description")
            search_args = {}
            param_desc = []
            for arg_key, param_key in combo.items():
                if param_key in params:
                    search_args[arg_key] = params[param_key]
                    if isinstance(params[param_key], list):
                        param_desc.append(f"{arg_key}=[{', '.join(params[param_key])}]")
                    else:
                        param_desc.append(f"{arg_key}={params[param_key]}")
            if search_args:
                print(f"\nRunning {description}: {', '.join(param_desc)}")
                results = self.search_structured(**search_args)
                if results:
                    key = description.replace("Structured search by ", "structured_")
                    search_results[key] = results
                    self.print_search_results(
                        results,
                        search_type=description,
                        search_params=", ".join(param_desc),
                        include_matches=include_matches,
                    )

        # Run hybrid searches
        hybrid_combinations = [
            {"query": "name", "description": "Hybrid search by name"},
            {
                "query": "name",
                "skills": "top_skills",
                "description": "Hybrid search by name with skills",
            },
            {
                "query": "name",
                "technologies": "top_technologies",
                "description": "Hybrid search by name with technologies",
            },
            {
                "query": "role",
                "company": "latest_company",
                "description": "Hybrid search by role and company",
            },
        ]
        for combo in hybrid_combinations:
            description = combo.pop("description")
            search_args = {}
            param_desc = []
            for arg_key, param_key in combo.items():
                if param_key in params:
                    value = params[param_key]
                    search_args[arg_key] = value
                    if isinstance(value, list):
                        param_desc.append(f"{arg_key}=[{', '.join(value)}]")
                    else:
                        param_desc.append(f"{arg_key}={value}")
            if search_args and "query" in search_args:
                print(f"\nRunning {description}: {', '.join(param_desc)}")
                results = self.search_hybrid(**search_args)
                if results:
                    key = description.replace("Hybrid search by ", "hybrid_")
                    search_results[key] = results
                    self.print_search_results(
                        results,
                        search_type=description,
                        search_params=", ".join(param_desc),
                        include_matches=include_matches,
                    )

        self.search_results = search_results
        return search_results

    def compare_search_results(self):
        """Compare results from different search methods"""
        if not self.search_results:
            print("No search results available to compare")
            return
        print("\n4. Search Results Comparison")
        print("=" * 80)
        cv_counts = {}
        method_counts = {}
        for method, results in self.search_results.items():
            method_counts[method] = len(results)
            for result in results:
                rid = result.get("resume_id") or result.get("cv_id")
                if rid:
                    if rid not in cv_counts:
                        cv_counts[rid] = {"total": 0, "methods": []}
                    cv_counts[rid]["total"] += 1
                    cv_counts[rid]["methods"].append(method)
        print(f"Total unique CVs found: {len(cv_counts)}")
        print(f"Search methods: {len(self.search_results)}")
        print("\nResults by search method:")
        for method, count in method_counts.items():
            print(f"  {method}: {count} results")
        print("\nCVs found by multiple methods:")
        for cv_id, data in sorted(cv_counts.items(), key=lambda x: x[1]["total"], reverse=True):
            if data["total"] > 1:
                print(f"  CV ID: {cv_id}")
                print(f"    Found by {data['total']} methods: {', '.join(data['methods'])}")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Fully automated CV processing and search testing")
    parser.add_argument(
        "--filename",
        default="./test_inputs/Max_Azatian_CV.pdf",
        help="Name of the file to process",
    )
    parser.add_argument("--backend-url", default="http://localhost:8000", help="URL for backend service")
    parser.add_argument("--search", action="store_true", help="Run search tests")
    parser.add_argument("--review", action="store_true", help="Show review data")
    parser.add_argument(
        "--full-json",
        action="store_true",
        help="Print full JSON output including match details",
    )
    args = parser.parse_args()

    print(f"Using backend service at: {args.backend_url}")
    print(f"Run search?: {args.search}")
    print(f"Show review?: {args.review}")
    print(f"Full JSON?: {args.full_json}")

    client = CVProcessingTest(backend_url=args.backend_url)
    client.process_file(args.filename)
    client.print_cv_summary()

    if args.review:
        client.print_review()

    if args.search:
        client.run_comprehensive_search(include_matches=args.full_json)
        client.compare_search_results()

    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
