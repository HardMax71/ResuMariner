from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "django_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "django_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

REDIS_QUEUE_LENGTH = Gauge("redis_queue_length", "Number of jobs in main queue")

REDIS_SCHEDULED_RETRIES = Gauge("redis_scheduled_retries", "Number of scheduled retry jobs")

REDIS_ACTIVE_JOBS = Gauge("redis_active_jobs", "Number of currently active jobs")

REDIS_MEMORY_USAGE = Gauge("redis_memory_usage_bytes", "Redis memory usage in bytes")

EMBEDDING_API_CALLS = Counter(
    "embedding_api_calls_total",
    "Total calls to embedding API",
    ["status", "batch_size"],
)

EMBEDDING_API_DURATION = Histogram(
    "embedding_api_duration_seconds",
    "Embedding API call duration",
    ["batch_size"],
)

LLM_API_CALLS = Counter(
    "llm_api_calls_total",
    "Total calls to LLM API",
    ["mode", "status"],
)

LLM_API_DURATION = Histogram(
    "llm_api_duration_seconds",
    "LLM API call duration",
    ["mode"],
)

QDRANT_CORRUPTED_POINTS = Counter(
    "qdrant_corrupted_points_total",
    "Total number of corrupted points in Qdrant (missing payload or uid)",
    ["corruption_type"],
)

RAG_GENERATION_COUNT = Counter(
    "rag_generation_total",
    "Total RAG generations",
    ["feature", "status"],
)

RAG_GENERATION_DURATION = Histogram(
    "rag_generation_duration_seconds",
    "RAG generation duration",
    ["feature"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

RAG_CACHE_HIT_COUNT = Counter(
    "rag_cache_hit_total",
    "RAG cache hits",
    ["feature"],
)

RAG_CACHE_MISS_COUNT = Counter(
    "rag_cache_miss_total",
    "RAG cache misses",
    ["feature"],
)

RAG_TOKEN_USAGE = Counter(
    "rag_token_usage_total",
    "Total tokens used by RAG features",
    ["feature", "token_type"],
)


def update_queue_metrics(stats: dict) -> None:
    """Update Redis queue metrics from stats dictionary."""
    REDIS_QUEUE_LENGTH.set(stats.get("queue_length", 0))
    REDIS_SCHEDULED_RETRIES.set(stats.get("scheduled_retries", 0))
    REDIS_ACTIVE_JOBS.set(stats.get("active_jobs", 0))
    REDIS_MEMORY_USAGE.set(stats.get("redis_memory_usage", 0))
