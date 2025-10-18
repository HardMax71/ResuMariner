<p align="center">
  <img src="frontend/public/icons/icon.png" alt="ResuMariner" width="128" height="128" />
</p>
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

This project started after one of those meetings where "simple resume parsing" evolved into "candidate matching with AI predictions." Instead of building another one-off script, I built a proper architecture that handles changing requirements. Neo4j for graph data, Qdrant for vector search, Django for the backend. Can scale from basic text extraction to complex queries without rewrites.

## What it does

The system handles CV uploads (PDF, DOCX, JPG formats), parses them into structured data, and makes them searchable. You can throw natural language queries at it ("find someone who's built payment systems") or search by specific criteria (5+ years Python, knows Docker, lives in Berlin). There's also a hybrid mode that combines both approaches when you need the flexibility of semantic search with the precision of structured filters.

## Architecture

V1 was microservices. Spent more time coordinating services than building features, plus the "single source of truth" problem for shared domain objects (Resume, AIReview) had no good solution - shared libs and copypasting both were bad. V2 is a Django monolith with clean separation through apps.

The processor app handles uploads and LLM parsing. CVs get queued in Redis, processed by background workers, and stored in two places. Neo4j holds the graph - candidates connecting to companies, skills, locations, education. Structured searches are just relationship traversals. Qdrant stores vector embeddings, with each resume chunked into multiple vectors (summary, skills, work bullets, projects) to avoid semantic soup. Searches match against all chunks independently, then group by candidate.

Traefik is the reverse proxy. Redis handles queuing, caching, and worker coordination. Workers run Django Q for async processing.

<p align="center">
  <img src="http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/HardMax71/ResuMariner/main/frontend/public/diagrams/infrastructure.puml" alt="System Architecture" />
</p>

## Getting started

You need Docker, Docker Compose, and at least 4GB of RAM. Grab an API key from OpenAI, Gemini, or whatever LLM provider you prefer - just one is enough. 
Copy `backend/.env.example` to `backend/.env` and drop your key in there.

Then run:
```bash
docker-compose up --build
```

The backend API will be at http://localhost:8000 and the Traefik dashboard at http://localhost:8080. Frontend will be at http://localhost:5173. 

## How the API works

Full OpenAPI spec at `/api/schema/`.

`POST /api/v1/upload/` returns a job ID immediately. Processing happens in the background - parsing PDFs, calling LLM APIs, generating embeddings takes time. Check status with `GET /api/v1/jobs/{job_id}/`, get results from `GET /api/v1/jobs/{job_id}/result/` once done.

### Search

Three endpoints, different approaches.

`POST /search/semantic/` takes natural language queries, converts them to embeddings, searches Qdrant's vector space. Ranked by semantic similarity. "Built payment systems in Python" matches "developed financial transaction services using Python" even without exact keywords.

`POST /search/structured/` takes exact criteria - years of experience, specific skills, locations. Queries Neo4j directly, traverses the graph. Fast and precise.

`POST /search/hybrid/` runs both in parallel, merges results with configurable weights. Useful for queries like "senior engineers" (semantic) who know "React, TypeScript, AWS" (structured).

`GET /filters/` returns searchable values - skills, locations, experience ranges from your actual data.

### Administrative endpoints

`POST /api/v1/jobs/cleanup/` purges old processing jobs. By default the system keeps results for 30 days, but this lets you manually trigger cleanup if needed. 
It also clears temporary files from uploads.

`GET /api/v1/health/` checks if the service is alive. It pings Redis, Neo4j, and Qdrant to make sure everything's actually reachable, not just that the web server is running.

## Testing

There's a test script that uploads a CV and runs all the different search types against it:

```bash
python ./backend/test_script.py path/to/resume.pdf
```

If you don't pass a path, it uses the example resume in [backend/test_inputs/Max_Azatian.pdf](backend/test_inputs/Max_Azatian_CV.pdf). Check [test_script.py](backend/test_script.py) for additional flags.

## License

MIT License - see [LICENSE](LICENSE) for details.
