<h1 align="center">ResuMariner</h1>

> We are looking for backend Python Developer for parsing project with unknown bounds and requirements. By the way, have you worked with RAGs and vector databases?
> 
> — *Undisclosed CTO during what was supposed to be a casual coffee chat*

This project started after one of those classic meetings where "simple resume parsing" mysteriously evolved into "enterprise-grade candidate matching with AI predictions." Instead of building yet another janky one-off script, I figured why not create a proper architecture that can actually handle whatever random requirements get tossed in next week? So here's ResuMariner - a solid microservice setup with Neo4j, Qdrant, and various APIs for handling CVs that can grow from "just extract the text" to "find me candidates with 7+ years React who once thought about learning Rust and might enjoy ping-pong" without needing a complete rewrite.
## ✨ Features

- **CV Upload and Processing**: Upload CV documents (PDF, DOCX, JPG) for automated parsing and analysis
- **Structured Data Extraction**: Extract key information from CVs into a structured format
- **CV Review Generation**: Generate professional reviews of candidate CVs
- **Semantic Search**: Find candidates based on natural language queries
- **Structured Search**: Search candidates by specific criteria (skills, experience, etc.)
- **Hybrid Search**: Combine semantic and structured search for optimal results
- **Secure Architecture**: Separation between public-facing and internal services

## 🏗️ Architecture

ResuMariner follows a microservices architecture with the following components:

![sys_diagram](https://github.com/user-attachments/assets/6415793d-88c4-46a4-bac0-6ba177c90da9)

- **Traefik**: Reverse proxy and API gateway
- **cv-intake-service**: Handles CV file uploads and job management
- **cv-processing-service**: Processes and analyzes CV documents using LLMs
- **cv-storage-service**: Manages persistent storage of CV data
- **cv-search-service**: Provides advanced search capabilities
- **Databases**:
  - **Neo4j**: Graph database for structured CV data
  - **Qdrant**: Vector database for semantic search embeddings
  - **Redis**: Job queue and caching

The system is split between a public network zone (accessible from outside) and a protected internal network zone.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- At least 4GB of RAM for running all services
- API keys for LLM providers (OpenAI, Gemini, etc.) if using those services (only one is enough)

### Deployment

Deployment is straightforward:
```bash
docker-compose up --build
```

That's it! The system will be available at the following endpoints:

- CV Upload: http://intake.localhost
- CV Search: http://search.localhost
- Traefik Dashboard: http://traefik.localhost

## 📋 API Documentation

### Upload API (intake.localhost)

- POST `/api/v1/upload`: Upload a CV file for processing
- GET `/api/v1/status/{job_id}`: Check processing status
- GET `/api/v1/results/{job_id}`: Get processing results

### Search API (search.localhost)

- POST `/search/semantic`: Semantic search using natural language
- POST `/search/structured`: Structured search using specific criteria
- POST `/search/hybrid`: Combined semantic and structured search
- GET `/filters`: Get available filter options

## 🧪 Testing

The system includes a comprehensive testing script that can process a CV and run various searches against it:

```bash 
python test_script.py path/to/resume.pdf
```

Calling 

```bash 
python test_script.py 
```

Will return result for existing CV in `./test_inputs` folder, namely `./test_inputs/Max_Azatian.pdf`.

Additional flags are to be found in [test_script.py](test_script.py).

<details>
<summary>Example output for provided CV</summary>

``` 
/Users/test/PycharmProjects/pythonProject/venv/bin/python /Users/test/PycharmProjects/ResuMariner/test_script.py 
Using intake service at: http://intake.localhost
Using search service at: http://search.localhost
No review?: False
No store?: False
No search?: False
Parallel?: False
Full JSON?: False
Processing file: ./test_inputs/Max_Azatian_CV.pdf

1. Uploading file to intake service...
Sending to: http://intake.localhost/api/v1/upload
Upload successful. Job ID: 730b6563-e5c3-476d-b535-d46b56a6ed32

Waiting for processing to complete...
 22%|██▏       | 13/60 [00:26<01:35,  2.03s/it]
Completed! Contents: {'job_id': '730b6563-e5c3-476d-b535-d46b56a6ed32', 'status': 'completed', 'created_at': '2025-03-02T23:05:18.196529', 'updated_at': '2025-03-02T23:05:43.193148', 'result_url': '/api/v1/results/730b6563-e5c3-476d-b535-d46b56a6ed32', 'error': ''}
Fetching result from: http://intake.localhost/api/v1/results/730b6563-e5c3-476d-b535-d46b56a6ed32
Processing completed! CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650

2. CV Summary:
================================================================================
2. CV Summary:
================================================================================
{
  "personal_info": {
    "name": "Max Azatian",
    "resume_lang": "en",
    "contact": {
      "email": "max.azatian@gmail.com",
      "phone": "tel:+49-178-1234567",
      "links": {
        "telegram": null,
        "linkedin": "https://www.linkedin.com/in/max-azatian/",
        "github": "https://github.com/HardMax71",
        "other_links": null
      }
    },
    "demographics": {
      "current_location": {
        "city": "Munich",
        "state": null,
        "country": "Germany"
      },
      "work_authorization": {
        "citizenship": "Germany",
        "work_permit": null,
        "visa_sponsorship_required": null
      }
    }
  },
  "professional_profile": {
    "summary": "Backend developer with experience in crafting efficient systems. Combine technical precision with teamwork to solve problems through a clean, maintainable design.",
    "preferences": {
      "role": "Software Engineer",
      "employment_types": [
        "full-time",
        "part-time",
        "contract"
      ],
      "work_modes": [
        "remote",
        "onsite",
        "hybrid"
      ],
      "salary": null
    }
  },
  "skills": [
    {
      "name": "Python"
    },
    {
      "name": "JavaScript"
    },
    {
      "name": "HTML/CSS"
    },
    {
      "name": "FastAPI"
    },
    {
      "name": "Flask"
    },
    {
      "name": "Django"
    },
    {
      "name": "ORM (SQLAlchemy)"
    },
    {
      "name": "Linters (Flake8, Ruff)"
    },
    {
      "name": "Locust"
    },
    {
      "name": "RESTful APIs"
    },
    {
      "name": "PostgreSQL"
    },
    {
      "name": "MongoDB"
    },
    {
      "name": "SQLite"
    },
    {
      "name": "Redis"
    },
    {
      "name": "Neo4j"
    },
    {
      "name": "Docker"
    },
    {
      "name": "Docker Compose"
    },
    {
      "name": "Kubernetes"
    },
    {
      "name": "Git"
    },
    {
      "name": "Linux"
    },
    {
      "name": "Cloud platforms (GCP, Azure)"
    },
    {
      "name": "Traefik"
    },
    {
      "name": "Prometheus"
    },
    {
      "name": "Grafana"
    }
  ],
  "employment_history": [
    {
      "company": {
        "name": "Self-employed",
        "url": null
      },
      "position": "Software Engineer (Part-time)",
      "employment_type": "part-time",
      "work_mode": "remote",
      "duration": {
        "date_format": "MM.YYYY",
        "start": "06.2021",
        "end": "current",
        "duration_months": 45
      },
      "location": {
        "city": "Munich",
        "state": null,
        "country": "Germany"
      },
      "key_points": [
        {
          "text": "Reached 90% pilot user adoption for pet salon booking system by developing Django/PostgreSQL MVP with auto scheduling, accompanied by Doxygen documentation featuring UML diagrams (class, activity, deployment)."
        },
        {
          "text": "Increased monthly active user growth by 40% for board game community platform via creating Django REST backend implementation supporting profile creation, blog posts, and filtered game searches with Bootstrap-based UI."
        }
      ],
      "tech_stack": [
        {
          "name": "Django"
        },
        {
          "name": "PostgreSQL"
        }
      ]
    }
  ],
  "projects": [
    {
      "title": "Integr8sCode",
      "url": "https://github.com/HardMax71/Integr8sCode",
      "tech_stack": [
        {
          "name": "Python"
        },
        {
          "name": "FastAPI"
        },
        {
          "name": "Pydantic"
        },
        {
          "name": "Kubernetes"
        },
        {
          "name": "Svelte"
        },
        {
          "name": "MongoDB"
        },
        {
          "name": "Prometheus"
        },
        {
          "name": "Grafana"
        }
      ],
      "key_points": [
        {
          "text": "Reduced memory usage by 25%, tracked in Prometheus, by enforcing per-pod CPU/memory limits (CPU: 100m, memory: 128Mi), adding auto-scaling policies (Horizontal Pod Autoscaler), and optimizing Docker layers (e.g., moving nonessential packages and using python:{version}-slim)."
        },
        {
          "text": "Achieved 30K+ daily script executions with an error rate below 0.3%, monitored via Grafana, by orchestrating ephemeral K8s pods and adding request validation with Pydantic."
        },
        {
          "text": "Raised backend test coverage to 92%, as measured by Codecov, by introducing unit/integration tests for critical modules and logging/reporting coverage in HTML reports."
        }
      ]
    }
  ],
  "education": [
    {
      "institution": {
        "name": "Technical University of Munich"
      },
      "qualification": "Master",
      "field": "Computer Science",
      "location": {
        "city": "Munich",
        "state": null,
        "country": "Germany"
      },
      "start": "10.2024",
      "end": "current",
      "status": "ongoing",
      "coursework": null,
      "extras": null
    },
    {
      "institution": {
        "name": "Technical University of Munich"
      },
      "qualification": "Bachelor",
      "field": "Computer Science",
      "location": {
        "city": "Munich",
        "state": null,
        "country": "Germany"
      },
      "start": "10.2019",
      "end": "08.2024",
      "status": "completed",
      "coursework": null,
      "extras": null
    }
  ],
  "courses": null,
  "certifications": null,
  "language_proficiency": [
    {
      "language": {
        "name": "English"
      },
      "self_assessed": "C1",
      "cefr": "C1"
    },
    {
      "language": {
        "name": "German"
      },
      "self_assessed": "C1",
      "cefr": "C1"
    },
    {
      "language": {
        "name": "Japanese"
      },
      "self_assessed": "B1",
      "cefr": "B1"
    }
  ],
  "awards": null,
  "scientific_contributions": null,
  "validation_metadata": {
    "text_characters_processed": 2864,
    "links_processed": 7,
    "anomalies": []
  }
}
================================================================================

CV Review:
================================================================================
{
  "personal_info": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": null
  },
  "professional_profile": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": null
  },
  "skills": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": null
  },
  "employment_history": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": "Consider adding more quantifiable achievements to further demonstrate impact."
  },
  "projects": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": null
  },
  "education": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": "Consider highlighting relevant coursework or thesis for the ongoing Master's program."
  },
  "courses": {
    "MUST": "Consider adding any relevant courses taken, including names, organizations, and completion years.",
    "SHOULD": null,
    "ADVISE": null
  },
  "certifications": {
    "MUST": "Consider adding any relevant certifications, including issuing organizations and dates.",
    "SHOULD": null,
    "ADVISE": null
  },
  "language_proficiency": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": null
  },
  "awards": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": null
  },
  "scientific_contributions": {
    "MUST": null,
    "SHOULD": null,
    "ADVISE": null
  }
}
================================================================================

3. Running comprehensive search testing

Extracted search parameters:
{
  "name": "Max Azatian",
  "email": "max.azatian@gmail.com",
  "all_skills": [
    "Python",
    "JavaScript",
    "HTML/CSS",
    "FastAPI",
    "Flask",
    "Django",
    "ORM (SQLAlchemy)",
    "Linters (Flake8, Ruff)",
    "Locust",
    "RESTful APIs",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "Redis",
    "Neo4j",
    "Docker",
    "Docker Compose",
    "Kubernetes",
    "Git",
    "Linux",
    "Cloud platforms (GCP, Azure)",
    "Traefik",
    "Prometheus",
    "Grafana"
  ],
  "top_skills": [
    "Python",
    "JavaScript",
    "HTML/CSS"
  ],
  "role": "Software Engineer",
  "city": "Munich",
  "country": "Germany",
  "location": "Munich, Germany",
  "companies": [
    "Self-employed"
  ],
  "latest_company": "Self-employed",
  "technologies": [
    "Traefik",
    "Qdrant",
    "LLM",
    "Pydantic",
    "PostgreSQL",
    "Neo4j",
    "Kubernetes",
    "Flet",
    "FastAPI",
    "MongoDB",
    "Django",
    "Docker",
    "Python",
    "Grafana",
    "Redis",
    "Prometheus",
    "Svelte"
  ],
  "top_technologies": [
    "Traefik",
    "Qdrant",
    "LLM"
  ]
}

Running Semantic search by name: Max Azatian
Sending to: http://search.localhost/search/semantic
Payload: {
  "query": "Max Azatian",
  "limit": 5,
  "min_score": 0.0
}
Found 1 results (semantic search):

Search Results (Semantic search by name):
Parameters: Max Azatian
================================================================================
1. CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 5
----------------------------------------
================================================================================

Running Semantic search by role: Software Engineer
Sending to: http://search.localhost/search/semantic
Payload: {
  "query": "Software Engineer",
  "limit": 5,
  "min_score": 0.0
}
Found 1 results (semantic search):

Search Results (Semantic search by role):
Parameters: Software Engineer
================================================================================
1. CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 5
----------------------------------------
================================================================================

Running Semantic search by company: Self-employed
Sending to: http://search.localhost/search/semantic
Payload: {
  "query": "Self-employed",
  "limit": 5,
  "min_score": 0.0
}
Found 1 results (semantic search):

Search Results (Semantic search by company):
Parameters: Self-employed
================================================================================
1. CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.6046
   Number of matches: 5
----------------------------------------
================================================================================

Running Semantic search by location: Munich, Germany
Sending to: http://search.localhost/search/semantic
Payload: {
  "query": "Munich, Germany",
  "limit": 5,
  "min_score": 0.0
}
Found 1 results (semantic search):

Search Results (Semantic search by location):
Parameters: Munich, Germany
================================================================================
1. CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 5
----------------------------------------
================================================================================

Running Semantic search by skills: Python, JavaScript, HTML/CSS
Sending to: http://search.localhost/search/semantic
Payload: {
  "query": "Python, JavaScript, HTML/CSS",
  "limit": 5,
  "min_score": 0.0
}
Found 1 results (semantic search):

Search Results (Semantic search by skills):
Parameters: Python, JavaScript, HTML/CSS
================================================================================
1. CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.4848
   Number of matches: 5
----------------------------------------
================================================================================

Running Structured search by top skills: skills=[Python, JavaScript, HTML/CSS]
Sending to: http://search.localhost/search/structured
Payload: {
  "limit": 5,
  "skills": [
    "Python",
    "JavaScript",
    "HTML/CSS"
  ]
}
Found 1 results (structured search):

Search Results (Structured search by top skills):
Parameters: skills=[Python, JavaScript, HTML/CSS]
================================================================================
1. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 0
----------------------------------------
================================================================================

Running Structured search by role: role=Software Engineer
Sending to: http://search.localhost/search/structured
Payload: {
  "limit": 5,
  "role": "Software Engineer"
}
Found 1 results (structured search):

Search Results (Structured search by role):
Parameters: role=Software Engineer
================================================================================
1. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 0
----------------------------------------
================================================================================

Running Structured search by company: company=Self-employed
Sending to: http://search.localhost/search/structured
Payload: {
  "limit": 5,
  "company": "Self-employed"
}
Found 1 results (structured search):

Search Results (Structured search by company):
Parameters: company=Self-employed
================================================================================
1. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 0
----------------------------------------
================================================================================

Running Structured search by skills and role: skills=[Python, JavaScript, HTML/CSS], role=Software Engineer
Sending to: http://search.localhost/search/structured
Payload: {
  "limit": 5,
  "skills": [
    "Python",
    "JavaScript",
    "HTML/CSS"
  ],
  "role": "Software Engineer"
}
Found 1 results (structured search):

Search Results (Structured search by skills and role):
Parameters: skills=[Python, JavaScript, HTML/CSS], role=Software Engineer
================================================================================
1. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 0
----------------------------------------
================================================================================

Running Structured search by technologies: technologies=[Traefik, Qdrant, LLM]
Sending to: http://search.localhost/search/structured
Payload: {
  "limit": 5,
  "technologies": [
    "Traefik",
    "Qdrant",
    "LLM"
  ]
}
Found 1 results (structured search):

Search Results (Structured search by technologies):
Parameters: technologies=[Traefik, Qdrant, LLM]
================================================================================
1. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 1.0000
   Number of matches: 0
----------------------------------------
================================================================================

Running Hybrid search by name: query=Max Azatian
Sending to: http://search.localhost/search/hybrid
Payload: {
  "query": "Max Azatian",
  "limit": 5,
  "vector_weight": 0.7,
  "graph_weight": 0.3
}
Found 2 results (hybrid search):

Search Results (Hybrid search by name):
Parameters: query=Max Azatian
================================================================================
1. CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.7000
   Number of matches: 10
----------------------------------------
2. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.3000
   Number of matches: 0
----------------------------------------
================================================================================

Running Hybrid search by name with skills: query=Max Azatian, skills=[Python, JavaScript, HTML/CSS]
Sending to: http://search.localhost/search/hybrid
Payload: {
  "query": "Max Azatian",
  "limit": 5,
  "vector_weight": 0.7,
  "graph_weight": 0.3,
  "skills": [
    "Python",
    "JavaScript",
    "HTML/CSS"
  ]
}
Found 1 results (hybrid search):

Search Results (Hybrid search by name with skills):
Parameters: query=Max Azatian, skills=[Python, JavaScript, HTML/CSS]
================================================================================
1. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.3000
   Number of matches: 0
----------------------------------------
================================================================================

Running Hybrid search by name with technologies: query=Max Azatian, technologies=[Traefik, Qdrant, LLM]
Sending to: http://search.localhost/search/hybrid
Payload: {
  "query": "Max Azatian",
  "limit": 5,
  "vector_weight": 0.7,
  "graph_weight": 0.3,
  "technologies": [
    "Traefik",
    "Qdrant",
    "LLM"
  ]
}
Found 2 results (hybrid search):

Search Results (Hybrid search by name with technologies):
Parameters: query=Max Azatian, technologies=[Traefik, Qdrant, LLM]
================================================================================
1. CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.7000
   Number of matches: 10
----------------------------------------
2. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.3000
   Number of matches: 0
----------------------------------------
================================================================================

Running Hybrid search by role and company: query=Software Engineer, company=Self-employed
Sending to: http://search.localhost/search/hybrid
Payload: {
  "query": "Software Engineer",
  "limit": 5,
  "vector_weight": 0.7,
  "graph_weight": 0.3,
  "company": "Self-employed"
}
Found 1 results (hybrid search):

Search Results (Hybrid search by role and company):
Parameters: query=Software Engineer, company=Self-employed
================================================================================
1. CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
   Name: Max Azatian
   Email: max.azatian@gmail.com
   Score: 0.3000
   Number of matches: 0
----------------------------------------
================================================================================

4. Search Results Comparison
================================================================================
Total unique CVs found: 2
Search methods: 14

Results by search method:
  semantic_name: 1 results
  semantic_role: 1 results
  semantic_latest_company: 1 results
  semantic_location: 1 results
  semantic_top_skills: 1 results
  structured_top skills: 1 results
  structured_role: 1 results
  structured_company: 1 results
  structured_skills and role: 1 results
  structured_technologies: 1 results
  hybrid_name: 2 results
  hybrid_name with skills: 1 results
  hybrid_name with technologies: 2 results
  hybrid_role and company: 1 results

CVs found by multiple methods:
  CV ID: 730b6563-e5c3-476d-b535-d46b56a6ed32
    Found by 9 methods: structured_top skills, structured_role, structured_company, structured_skills and role, structured_technologies, hybrid_name, hybrid_name with skills, hybrid_name with technologies, hybrid_role and company
  CV ID: f0ffd328-ed4c-4e80-8b77-f4ab1b7b6650
    Found by 7 methods: semantic_name, semantic_role, semantic_latest_company, semantic_location, semantic_top_skills, hybrid_name, hybrid_name with technologies
================================================================================

Test completed successfully!

Process finished with exit code 0
```

</details>


## 📖 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
