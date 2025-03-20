import argparse
import itertools
import json
import os
import sys
import time

import requests
from tqdm import tqdm


class CVProcessingTest:

    def __init__(self, intake_url="http://intake.localhost", search_url="http://search.localhost"):
        """Initialize with service URLs"""
        self.intake_url = intake_url
        self.search_url = search_url
        self.cv_id = None
        self.cv_data = None
        self.review_data = None
        self.search_results = {}

    def process_file(self, file_path, parallel=False, generate_review=True, store_in_db=True):
        """Process a CV file through the pipeline via the intake service"""
        print(f"Processing file: {file_path}")

        # Validate file exists
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found")
            sys.exit(1)

        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        print("\n1. Uploading file to intake service...")
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (file_name, file, self._get_mime_type(file_ext))}
                data = {
                    'parallel': str(parallel).lower(),
                    'generate_review': str(generate_review).lower(),
                    'store_in_db': str(store_in_db).lower()
                }
                print(f"Sending to: {self.intake_url}/api/v1/upload")
                response = requests.post(
                    f"{self.intake_url}/api/v1/upload",
                    files=files,
                    data=data,
                    timeout=180  # 3-minute timeout for processing
                )

                if response.status_code != 200:
                    print(f"Upload failed with status {response.status_code}: {response.text}")
                    sys.exit(1)

                upload_result = response.json()
                job_id = upload_result.get('job_id')

                if not job_id:
                    print("Error: No job ID returned from upload")
                    sys.exit(1)

                print(f"Upload successful. Job ID: {job_id}")

            # Poll for processing completion
            print("\nWaiting for processing to complete...")
            max_retries = 60
            retry_interval = 2  # seconds

            for i in tqdm(range(max_retries)):
                response = requests.get(
                    f"{self.intake_url}/api/v1/status/{job_id}",
                    timeout=10
                )

                if response.status_code != 200:
                    print(f"Status check failed: {response.status_code} - {response.text}")
                    time.sleep(retry_interval)
                    continue

                status = response.json()
                if status.get('status') == 'completed':
                    print("Completed! Contents:", status)
                    # If no 'data' key is present but there is a result_url, fetch the result
                    if 'result_url' in status and not status.get('data'):
                        result_url = status['result_url']
                        full_result_url = f"{self.intake_url}{result_url}"
                        print(f"Fetching result from: {full_result_url}")
                        result_response = requests.get(full_result_url, timeout=30)
                        if result_response.status_code != 200:
                            print(f"Failed to get result: {result_response.status_code} - {result_response.text}")
                            sys.exit(1)
                        result_data = result_response.json()
                    else:
                        result_data = status.get('data', {})

                    # Extract CV ID from metadata, structured data, and review
                    self.cv_id = result_data.get('metadata', {}).get('cv_id')
                    self.cv_data = result_data.get('structured_data')
                    self.review_data = result_data.get('review')

                    print(f"Processing completed! CV ID: {self.cv_id}")
                    return result_data
                elif status.get('status') == 'failed':
                    print(f"Processing failed: {status.get('message')}")
                    sys.exit(1)

                time.sleep(retry_interval)

            print("Error: Processing timed out")
            sys.exit(1)

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            sys.exit(1)

    def extract_search_parameters(self):
        """Extract various search parameters from the CV data"""
        if not self.cv_data:
            return {}

        params = {}

        # Extract name
        if self.cv_data.get('personal_info', {}).get('name'):
            params['name'] = self.cv_data['personal_info']['name']

        # Extract email
        if self.cv_data.get('personal_info', {}).get('contact', {}).get('email'):
            params['email'] = self.cv_data['personal_info']['contact']['email']

        # Extract skills (all and top 3)
        if self.cv_data.get('skills'):
            # Extract skill names from skill objects
            skill_names = [skill.get('name') for skill in self.cv_data['skills']]
            params['all_skills'] = skill_names
            params['top_skills'] = skill_names[:min(3, len(skill_names))]

        # Extract role
        if self.cv_data.get('professional_profile', {}).get('preferences', {}).get('role'):
            params['role'] = self.cv_data['professional_profile']['preferences']['role']

        # Extract location
        location = self.cv_data.get('personal_info', {}).get('demographics', {}).get('current_location', {})
        if location:
            location_parts = []
            if location.get('city'):
                params['city'] = location['city']
                location_parts.append(location['city'])
            if location.get('country'):
                params['country'] = location['country']
                location_parts.append(location['country'])
            if location_parts:
                params['location'] = ', '.join(location_parts)

        # Extract companies
        if self.cv_data.get('employment_history'):
            companies = [job.get('company') for job in self.cv_data['employment_history'] if job.get('company')]
            if companies:
                params['companies'] = companies
                params['latest_company'] = companies[0]  # Assuming most recent is first

        # Extract technologies
        tech_lists = []
        if self.cv_data.get('employment_history'):
            for job in self.cv_data['employment_history']:
                if job.get('tech_stack'):
                    # Extract name from each technology dictionary
                    tech_list = [tech.get('name') for tech in job['tech_stack'] if
                                 isinstance(tech, dict) and 'name' in tech]
                    tech_lists.append(tech_list)
        if self.cv_data.get('projects'):
            for project in self.cv_data['projects']:
                if project.get('tech_stack'):
                    # Extract name from each technology dictionary
                    tech_list = [tech.get('name') for tech in project['tech_stack'] if
                                 isinstance(tech, dict) and 'name' in tech]
                    tech_lists.append(tech_list)
        if tech_lists:
            technologies = list(set(itertools.chain.from_iterable(tech_lists)))
            if technologies:
                params['technologies'] = technologies
                params['top_technologies'] = technologies[:min(3, len(technologies))]

        return params

    def search_semantic(self, query, limit=5, min_score=0.0, filters=None):
        """Perform semantic search"""
        try:
            search_payload = {
                "query": query,
                "limit": limit,
                "min_score": min_score
            }
            if filters:
                search_payload["filters"] = filters

            print(f"Sending to: {self.search_url}/search/semantic")
            print(f"Payload: {json.dumps(search_payload, indent=2)}")
            response = requests.post(
                f"{self.search_url}/search/semantic",
                json=search_payload,
                timeout=30
            )
            if response.status_code != 200:
                print(f"Semantic search failed: {response.status_code} - {response.text}")
                return None

            search_results = response.json()
            results = search_results.get('results', [])
            if not results:
                print("No results found")
                return None

            print(f"Found {len(results)} results (semantic search):")
            return results

        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return None

    def search_structured(self, skills=None, technologies=None, role=None,
                          company=None, location=None, years_experience=None,
                          limit=5):
        """Perform structured search"""
        try:
            search_payload = {"limit": limit}
            if skills:
                search_payload["skills"] = skills if isinstance(skills, list) else [skills]
            if technologies:
                search_payload["technologies"] = technologies if isinstance(technologies, list) else [technologies]
            if role:
                search_payload["role"] = role
            if company:
                search_payload["company"] = company.get("name") if isinstance(company, dict) else company
            if location:
                search_payload["location"] = location
            if years_experience is not None:
                search_payload["years_experience"] = years_experience

            print(f"Sending to: {self.search_url}/search/structured")
            print(f"Payload: {json.dumps(search_payload, indent=2)}")
            response = requests.post(
                f"{self.search_url}/search/structured",
                json=search_payload,
                timeout=30
            )
            if response.status_code != 200:
                print(f"Structured search failed: {response.status_code} - {response.text}")
                return None

            search_results = response.json()
            results = search_results.get('results', [])
            if not results:
                print("No results found")
                return None

            print(f"Found {len(results)} results (structured search):")
            return results

        except Exception as e:
            print(f"Error in structured search: {str(e)}")
            return None

    def search_hybrid(self, query, skills=None, technologies=None, role=None,
                      company=None, location=None, vector_weight=0.7,
                      graph_weight=0.3, limit=5):
        """Perform hybrid search combining semantic and structured approaches"""
        try:
            search_payload = {
                "query": query,
                "limit": limit,
                "vector_weight": vector_weight,
                "graph_weight": graph_weight
            }
            if skills:
                search_payload["skills"] = skills if isinstance(skills, list) else [skills]
            if technologies:
                search_payload["technologies"] = technologies if isinstance(technologies, list) else [technologies]
            if role:
                search_payload["role"] = role
            if company:
                search_payload["company"] = company.get("name") if isinstance(company, dict) else company
            if location:
                search_payload["location"] = location

            print(f"Sending to: {self.search_url}/search/hybrid")
            print(f"Payload: {json.dumps(search_payload, indent=2)}")
            response = requests.post(
                f"{self.search_url}/search/hybrid",
                json=search_payload,
                timeout=30
            )
            if response.status_code != 200:
                print(f"Hybrid search failed: {response.status_code} - {response.text}")
                return None

            search_results = response.json()
            results = search_results.get('results', [])
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
            print(f"Retrieving filter options from: {self.search_url}/filters")
            response = requests.get(f"{self.search_url}/filters", timeout=30)
            if response.status_code != 200:
                print(f"Failed to get filter options: {response.status_code} - {response.text}")
                return None
            filter_options = response.json()
            return filter_options

        except Exception as e:
            print(f"Error getting filter options: {str(e)}")
            return None

    def _get_mime_type(self, extension):
        """Get MIME type for file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
        }
        return mime_types.get(extension, 'application/octet-stream')

    def print_cv_summary(self):
        """Print a summary of the CV"""
        if not self.cv_data:
            print("No CV data available")
            return
        print("\n2. CV Summary:")
        print("=" * 80)
        print(json.dumps(self.cv_data, indent=2))
        print("=" * 80)

    def print_review(self):
        """Print the review of the CV"""
        if not self.review_data:
            print("No review data available")
            return
        print("\nCV Review:")
        print("=" * 80)
        print(json.dumps(self.review_data, indent=2))
        print("=" * 80)

    def print_search_results(self, results, search_type="", search_params="", include_matches=False):
        """Print search results with optional match details"""
        if not results:
            return
        print(f"\nSearch Results ({search_type}):")
        if search_params:
            print(f"Parameters: {search_params}")
        print("=" * 80)
        if include_matches:
            print(json.dumps(results, indent=2))
        else:
            for idx, result in enumerate(results):
                print(f"{idx + 1}. CV ID: {result.get('cv_id')}")
                print(f"   Name: {result.get('person_name')}")
                print(f"   Email: {result.get('email')}")
                print(f"   Score: {result.get('score'):.4f}")
                print(f"   Number of matches: {len(result.get('matches', []))}")
                print("-" * 40)
        print("=" * 80)

    def run_comprehensive_search(self, include_matches=False):
        """Run a comprehensive set of searches using all available parameters from the CV"""
        if not self.cv_data:
            print("No CV data available for searching")
            return {}
        print("\n3. Running comprehensive search testing")
        params = self.extract_search_parameters()
        print("\nExtracted search parameters:")
        print(json.dumps(params, indent=2))
        search_results = {}

        # Run semantic searches
        semantic_categories = {
            "name": "Semantic search by name",
            "role": "Semantic search by role",
            "latest_company": "Semantic search by company",
            "location": "Semantic search by location",
            "top_skills": "Semantic search by skills"
        }
        for key, description in semantic_categories.items():
            if key in params:
                query = params[key]
                if isinstance(query, dict):
                    query = query.get("name", "")
                elif isinstance(query, list):
                    # Also check if list items are dicts and convert them
                    query = ", ".join(
                        item.get("name", str(item)) if isinstance(item, dict) else str(item) for item in query)
                print(f"\nRunning {description}: {query}")
                results = self.search_semantic(query)
                if results:
                    search_results[f"semantic_{key}"] = results
                    self.print_search_results(results, search_type=description, search_params=query,
                                              include_matches=include_matches)

        # Run structured searches
        structured_combinations = [
            {"skills": "top_skills", "description": "Structured search by top skills"},
            {"role": "role", "description": "Structured search by role"},
            {"company": "latest_company", "description": "Structured search by company"},
            {"skills": "top_skills", "role": "role", "description": "Structured search by skills and role"},
            {"technologies": "top_technologies", "description": "Structured search by technologies"}
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
                    self.print_search_results(results, search_type=description, search_params=", ".join(param_desc),
                                              include_matches=include_matches)

        # Run hybrid searches
        hybrid_combinations = [
            {"query": "name", "description": "Hybrid search by name"},
            {"query": "name", "skills": "top_skills", "description": "Hybrid search by name with skills"},
            {"query": "name", "technologies": "top_technologies", "description": "Hybrid search by name with technologies"},
            {"query": "role", "company": "latest_company", "description": "Hybrid search by role and company"}
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
                    self.print_search_results(results, search_type=description, search_params=", ".join(param_desc),
                                              include_matches=include_matches)

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
                cv_id = result.get("cv_id")
                if cv_id:
                    if cv_id not in cv_counts:
                        cv_counts[cv_id] = {"total": 0, "methods": []}
                    cv_counts[cv_id]["total"] += 1
                    cv_counts[cv_id]["methods"].append(method)
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
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Fully automated CV processing and search testing')
    parser.add_argument('--filename', default='./test_inputs/Max_Azatian_CV.pdf', help='Name of the file to process')
    parser.add_argument('--intake-url', default='http://intake.localhost', help='URL for intake service')
    parser.add_argument('--search-url', default='http://search.localhost', help='URL for search service')
    parser.add_argument('--no-review', action='store_true', help='Skip generating review')
    parser.add_argument('--no-store', action='store_false', help='Skip storing in database')
    parser.add_argument('--no-search', action='store_true', help='Skip searching')
    parser.add_argument('--full-json', action='store_true', help='Print full JSON output including match details')
    parser.add_argument('--parallel', action='store_true', help='Use parallel processing')

    args = parser.parse_args()

    print(f"Using intake service at: {args.intake_url}")
    print(f"Using search service at: {args.search_url}")
    print(f"No review?: {args.no_review}")
    print(f"No store?: {args.no_store}")
    print(f"No search?: {args.no_search}")
    print(f"Parallel?: {args.parallel}")
    print(f"Full JSON?: {args.full_json}")

    client = CVProcessingTest(
        intake_url=args.intake_url,
        search_url=args.search_url
    )

    # Process file via intake service
    client.process_file(
        args.filename,
        parallel=args.parallel,
        generate_review=not args.no_review,
        store_in_db=not args.no_store
    )

    # Print CV summary
    client.print_cv_summary()

    # Print review if available
    if not args.no_review:
        client.print_review()

    # Run comprehensive search testing if not skipped
    if not args.no_store and not args.no_search:
        client.run_comprehensive_search(include_matches=args.full_json)
        client.compare_search_results()

    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
