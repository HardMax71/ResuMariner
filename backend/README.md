# Backend

## What this thing does

You know how finding the right candidate from a pile of resumes is like searching for a needle in a haystack? 
This system turns that haystack into a neatly organized part of the project where you can actually find what you're looking for.

It takes resumes (PDFs, images, whatever), understands them deeply using LLMs, 
breaks them into meaningful chunks, creates embeddings for semantic search, stores everything in a graph database for relationship queries, 
and lets you search using natural language like "Python developer with microservices experience" instead of hoping someone used the exact keywords you're searching for.

[!NOTE] [Pydantic-ai](https://ai.pydantic.dev/) is used for calling 3rd party LLM APIs (by default - OpenAI), feel free to change `LLM_*` data in `.env`
file in case if other provider is needed. 

## The architecture that makes it tick

The whole thing is built on Django because, honestly, Django just works. 
No need to reinvent auth, migrations, or admin panels when Django gives you all that for free.

### Core components

**Processor app** - This is where the magic starts. Upload a resume, it queues a job in Redis, extracts text with pdfplumber or OCR, sends it to an LLM (OpenAI's GPT-4o-mini) to structure it properly, then generates a review of what could be improved. The structured data is what makes everything else possible.

**Storage app** - Once we have structured data, it goes two places. Neo4j stores the actual resume data as a graph (people connected to companies and skills), while Qdrant stores embedding vectors for semantic search. The graph gives us relationship queries ("who worked at Google?"), vectors give us semantic similarity ("find someone like this person").

**Search app** - This is where it all comes together. You can do semantic search (vector similarity), structured search (graph queries), or hybrid search (both combined). The results show not just who matched, but exactly which parts of their resume matched and why.

**Core domain models** - All the Pydantic models live here. `Resume`, `PersonalInfo`, `EmploymentHistoryItem`, `Skill`, you name it. These models are the contract between all the services. Change them carefully.

### The processing pipeline

Here's what happens when someone uploads a resume:

1. File hits the `/api/v1/upload/` endpoint
2. Gets validated (size, type, signature check)
3. Job gets queued in Redis with a unique ID
4. Worker picks it up and starts processing
5. PDF parser extracts text and links
6. LLM structures the raw text into our domain model
7. Another LLM generates a review with suggestions
8. Text gets chunked and converted to embeddings
9. Everything gets stored in Neo4j and Qdrant
10. Job status updates to "completed" with results

The beauty is each step can fail independently without killing the whole pipeline. PDF parsing fails? We'll try OCR. LLM times out? We retry with exponential backoff. Storage fails? We mark it as failed but keep the structured data.

## Why the weird architectural choices

**Why multiple vectors per resume?** - I tried the single vector approach first. Complete disaster.
A resume isn't a tweet - it's got skills, multiple jobs, projects, education. Mashing all that into one vector gives you semantic soup. 
Now each meaningful chunk gets its own vector. Way more storage, but search actually works. [Read the full story here](docs/vector-search-architecture.md).

**Why Neo4j AND Qdrant?** - They solve different problems. Neo4j is incredible for relationship queries ("people who worked with John at Google"). 
Qdrant is perfect for semantic similarity ("resumes similar to this text"). Trying to do both with one database is like using a hammer as a screwdriver.

**Why chunk with metadata?** - A bullet point saying "reduced latency by 50%" means nothing without context. Was that for a Python backend? 
A React frontend? By keeping metadata about where each chunk came from, search results actually make sense.

**Why Django instead of FastAPI?** - Started with FastAPI microservices. Four services, four repos, service discovery, API gateways... nightmare. 
Django gives us one codebase, shared models, built-in admin, migrations, and it's still plenty fast. Sometimes boring is better.

## Setting it up

### Requirements

- Python 3.11+ (because we use the latest type hints)
- Redis (for job queuing)
- Neo4j (for graph storage)
- Qdrant (for vector search)
- An OpenAI API key (or compatible provider)

### Local development

```bash
# Clone and enter the directory
git clone <repo>
cd backend

# Install dependencies with uv (it's faster than pip)
uv pip install -e .

# Copy env and add your API keys
cp .env.example .env
# Edit .env with your OpenAI key and service credentials

# Run migrations
python manage.py migrate

# Start services with Docker
docker-compose up -d neo4j qdrant redis

# Run the server
python manage.py runserver

# In another terminal, start the worker
python manage.py intake_worker
```

### Docker setup

```bash
# Just run everything
docker-compose up

# Or build fresh
docker-compose up --build
```

API (by default) is available at: http://localhost:8000 .

## API examples that actually work

### Upload a resume

```bash
curl -X POST http://localhost:8000/api/v1/upload/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"

# Returns: {"job_id": "abc123", "status": "queued"}
```

### Check processing status

```bash
curl http://localhost:8000/api/v1/jobs/abc123/

# Returns: {"status": "completed", "progress": 100, ...}
```

### Search semantically

```bash
curl -X POST http://localhost:8000/search/semantic/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer with AWS experience", "limit": 5}'

# Returns matching resumes with relevant excerpts
```

### Search by structure

```bash
curl -X POST http://localhost:8000/search/structured/ \
  -H "Content-Type: application/json" \
  -d '{"filters": {"skills": ["Python", "Django"], "years_experience": 3}}'

# Returns resumes matching the criteria
```

## Things that will trip you up

**LLM rate limits** - The system retries with exponential backoff, but if you're processing hundreds of resumes, you'll hit limits. Consider batching or using multiple API keys.

**Neo4j memory** - Graph databases love RAM. If imports are slow, check Neo4j's heap size. The default is often too small.

**Embedding dimensions** - We use OpenAI's text-embedding-3-small (1536 dimensions). If you switch models, you'll need to recreate the Qdrant collection with the right dimensions.

**File size limits** - Default max is 10MB. Most resumes are under 1MB, but some people upload their entire portfolio. Adjust `MAX_FILE_SIZE` if needed.

**Docker networking** - Services inside Docker use hostnames (neo4j:7687). From your host machine, use localhost. This trips everyone up at least once.

## Testing philosophy

Tests focus on E2E flows that actually matter. Can we upload a file? Does search return results? Do the endpoints exist?

We explicitly DON'T test:
- Database connections (that's what health checks are for)
- External service availability
- Implementation details that change constantly

Run tests with:
```bash
python manage.py test
```
