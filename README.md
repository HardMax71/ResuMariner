<h1 align="center">ResuMariner</h1>
<p align="center">
  <a href="https://github.com/HardMax71/ResuMariner/actions/workflows/tests.yml">
    <img src="https://github.com/HardMax71/ResuMariner/actions/workflows/tests.yml/badge.svg" alt="Tests" />
  </a>
  <a href="https://github.com/HardMax71/ResuMariner/actions/workflows/mypy.yml">
    <img src="https://github.com/HardMax71/ResuMariner/actions/workflows/mypy.yml/badge.svg" alt="MyPy" />
  </a>
  <a href="https://github.com/HardMax71/ResuMariner/actions/workflows/ruff.yml">
    <img src="https://github.com/HardMax71/ResuMariner/actions/workflows/ruff.yml/badge.svg" alt="Ruff" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python Version" />
  </a>
  <a href="https://github.com/HardMax71/ResuMariner">
    <img src="https://img.shields.io/badge/django-5.1-green" alt="Django Version" />
  </a>
</p>


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

ResuMariner v2 has been refactored from microservices to a Django monolith for improved maintainability and simplified deployment:

- **Backend (Django Monolith)**: Consolidates all previous microservices into a single Django application with:
  - **Processor App**: Handles CV file uploads, parsing and LLM-based processing
  - **Storage App**: Manages persistence to Neo4j and Qdrant databases
  - **Search App**: Provides semantic, structured and hybrid search capabilities
  - **Core Module**: Shared domain models and services
- **Traefik**: Reverse proxy and API gateway
- **Databases**:
  - **Neo4j**: Graph database for structured CV data and relationships
  - **Qdrant**: Vector database for semantic search embeddings
  - **Redis**: Job queue, caching and worker coordination
- **Workers**: Async background processing for CV parsing and storage operations

The monolithic architecture simplifies deployment while maintaining clear separation of concerns through Django apps.

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

- Backend API: http://localhost:8000
- Traefik Dashboard: http://localhost:8080

## 📚 API Documentation

The backend exposes a REST API at http://localhost:8000. If you want the full OpenAPI spec, hit `/api/schema/` and you'll get the complete schema.

### How the API works

When you upload a CV through `POST /api/v1/upload/`, the system doesn't make you wait around. It immediately returns a job ID and throws the processing work onto a Redis queue. This is intentional - parsing PDFs, running them through language models, and generating embeddings takes time. Nobody wants to hold an HTTP connection open for 30 seconds.

You can check on your job with `GET /api/v1/jobs/{job_id}/`. It'll tell you if it's still churning away or if something went wrong. Once it's done, `GET /api/v1/jobs/{job_id}/result/` gives you the full structured CV data - everything from contact info to a detailed breakdown of work experience.

### The search endpoints

The interesting part is the search. We've got three flavors, each with its own strengths.

`POST /search/semantic/` is where you throw natural language at it. "Find me someone who's built payment systems in Python" - that kind of thing. Under the hood, it's converting your query to embeddings and searching through our vector space in Qdrant. The results come back ranked by semantic similarity, which often surfaces candidates you wouldn't find with keyword matching.

`POST /search/structured/` is the opposite approach. You know exactly what you want - 5+ years experience, specific skills, certain locations. This hits our Neo4j graph database and traverses relationships to find exact matches. It's fast and precise when you have clear criteria.

`POST /search/hybrid/` combines both approaches. I originally built this because recruiters kept asking for "senior engineers" (which is semantic) who know "React, TypeScript, and AWS" (which is structured). The hybrid endpoint runs both searches in parallel and merges the results with configurable weights. You can dial up the semantic side if you want more exploratory results, or lean on structured search when you need precision.

There's also `GET /filters/` which tells you what's actually searchable in the structured search. It pulls available skills, locations, and experience ranges from the data we've already processed. Useful if you're building a search UI and want to populate dropdowns.

### Administrative stuff

`POST /api/v1/jobs/cleanup/` triggers a cleanup of old processing jobs. By default, we keep results around for 30 days, but this lets you manually purge them if needed. It also cleans up any temporary files from the upload process.

The health check at `GET /api/v1/health/` is pretty basic - just returns a 200 if the service is up. But it also checks that Redis, Neo4j, and Qdrant are reachable, so it's actually a decent indicator that the whole system is functional.

## 🧪 Testing

The system includes a comprehensive testing script that can process a CV and run various searches against it:

```bash 
python ./backend/test_script.py path/to/resume.pdf
```

Calling 

```bash 
python ./backend/test_script.py 
```

Will return result for existing CV in `./test_inputs` folder, namely `./test_inputs/Max_Azatian.pdf`.

Additional flags are to be found in [test_script.py](backend/test_script.py).

## 📖 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
