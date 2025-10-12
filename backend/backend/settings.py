import os
import uuid
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from neomodel import config as neomodel_config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from backend directory
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ Loaded .env from {env_file}")
else:
    # Check if we're in GitHub Actions
    if os.getenv("GITHUB_ACTIONS"):
        print("✓ Running in GitHub Actions with secrets")
    else:
        print(f"⚠ No .env file found at {env_file}")
        print("  Using environment variables or defaults")

# =============================================================================
# CORE DJANGO SETTINGS
# =============================================================================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY must be set in environment")

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "silk",
    "drf_spectacular",
    "core",
    "processor",
    "search",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "silk.middleware.SilkyMiddleware",
    "core.middleware.DatabaseServicesMiddleware",
    "core.middleware.PrometheusMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "backend.asgi.application"

# =============================================================================
# DATABASE (Minimal - we use Neo4j/Qdrant directly)
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =============================================================================
# AUTHENTICATION & SECURITY
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# API Security
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ImproperlyConfigured("API_KEY must be set in environment")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ImproperlyConfigured("JWT_SECRET must be set in environment")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# CORS
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "false").lower() == "true"
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()]

# =============================================================================
# REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ResuMariner API",
    "DESCRIPTION": "CV Processing and Search API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# =============================================================================
# NEO4J GRAPH DATABASE
# =============================================================================

NEO4J_HOST = os.getenv("NEO4J_HOST", "neo4j")
NEO4J_PORT = int(os.getenv("NEO4J_PORT", "7687"))
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_URI = f"bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@{NEO4J_HOST}:{NEO4J_PORT}"
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
NEO4J_MAX_CONNECTION_LIFETIME = int(os.getenv("NEO4J_MAX_CONNECTION_LIFETIME", "3600"))
NEO4J_MAX_CONNECTION_POOL_SIZE = int(os.getenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "50"))
NEO4J_CONNECTION_TIMEOUT = int(os.getenv("NEO4J_CONNECTION_TIMEOUT", "30"))

neomodel_config.DATABASE_URL = NEO4J_URI

# =============================================================================
# QDRANT VECTOR DATABASE
# =============================================================================

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "cv_key_points")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "1536"))
QDRANT_TIMEOUT = int(os.getenv("QDRANT_TIMEOUT", "30"))
QDRANT_PREFER_GRPC = os.getenv("QDRANT_PREFER_GRPC", "False").lower() == "true"

# =============================================================================
# REDIS
# =============================================================================

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
WORKER_CONCURRENT_JOBS = int(os.getenv("WORKER_CONCURRENT_JOBS", "10"))
REDIS_JOB_PREFIX = os.getenv("REDIS_JOB_PREFIX", "cv:job:")
REDIS_JOB_TIMEOUT = int(os.getenv("REDIS_JOB_TIMEOUT", "1800"))
REDIS_MAX_RETRIES = int(os.getenv("REDIS_MAX_RETRIES", "3"))

# =============================================================================
# LLM CONFIGURATION (REQUIRED)
# =============================================================================

# Text LLM
TEXT_LLM_PROVIDER = os.getenv("TEXT_LLM_PROVIDER", "openai")
TEXT_LLM_MODEL = os.getenv("TEXT_LLM_MODEL", "gpt-4o-mini")
TEXT_LLM_API_KEY = os.getenv("TEXT_LLM_API_KEY", "")
TEXT_LLM_BASE_URL = os.getenv("TEXT_LLM_BASE_URL", "")

# OCR LLM
OCR_LLM_PROVIDER = os.getenv("OCR_LLM_PROVIDER", "openai")
OCR_LLM_MODEL = os.getenv("OCR_LLM_MODEL", "gpt-4o-mini")
OCR_LLM_API_KEY = os.getenv("OCR_LLM_API_KEY", "")
OCR_LLM_BASE_URL = os.getenv("OCR_LLM_BASE_URL", "")

# LLM Settings
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
MAX_TOKENS_IN_RESUME_TO_PROCESS = int(os.getenv("MAX_TOKENS_IN_RESUME_TO_PROCESS", "5000"))

# LLM Usage Limits
LLM_REQUEST_LIMIT = int(os.getenv("LLM_REQUEST_LIMIT", "10"))
LLM_REQUEST_TOKENS_LIMIT = int(os.getenv("LLM_REQUEST_TOKENS_LIMIT", "100000"))

# Embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_TIMEOUT = float(os.getenv("EMBEDDING_TIMEOUT", "60.0"))
EMBEDDING_BATCH_TIMEOUT = float(os.getenv("EMBEDDING_BATCH_TIMEOUT", "120.0"))
EMBEDDING_MAX_BATCH_SIZE = int(os.getenv("EMBEDDING_MAX_BATCH_SIZE", "64"))
EMBEDDING_CIRCUIT_BREAKER_FAIL_MAX = int(os.getenv("EMBEDDING_CIRCUIT_BREAKER_FAIL_MAX", "3"))
EMBEDDING_CIRCUIT_BREAKER_RESET_TIMEOUT = int(os.getenv("EMBEDDING_CIRCUIT_BREAKER_RESET_TIMEOUT", "30"))


# =============================================================================
# SEARCH
# =============================================================================

DEFAULT_VECTOR_WEIGHT = float(os.getenv("DEFAULT_VECTOR_WEIGHT", "0.7"))
DEFAULT_GRAPH_WEIGHT = float(os.getenv("DEFAULT_GRAPH_WEIGHT", "0.3"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

# =============================================================================
# WORKER
# =============================================================================

WORKER_ID = os.getenv("WORKER_ID", f"worker-{uuid.uuid4().hex[:8]}")
WORKER_STORE_IN_DB = os.getenv("WORKER_STORE_IN_DB", "true").lower() == "true"
WORKER_GENERATE_REVIEW = os.getenv("WORKER_GENERATE_REVIEW", "true").lower() == "true"
WORKER_CONCURRENT_JOBS = int(os.getenv("WORKER_CONCURRENT_JOBS", "3"))

REDIS_COMPLETED_JOB_TTL = int(os.getenv("REDIS_COMPLETED_JOB_TTL", "3600"))  # 1 hour
REDIS_FAILED_JOB_TTL = int(os.getenv("REDIS_FAILED_JOB_TTL", "21600"))  # 6 hours
REDIS_PROCESSING_JOB_TTL = int(os.getenv("REDIS_PROCESSING_JOB_TTL", "86400"))  # 24 hours

# =============================================================================
# STORAGE
# =============================================================================

DURABLE_STORAGE = os.getenv("DURABLE_STORAGE", "local")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/cv_uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
MIN_FILE_SIZE = int(os.getenv("MIN_FILE_SIZE", "1024"))  # 1KB

# S3 Storage settings (always define for compatibility)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", "")
AWS_DEFAULT_ACL = None

# =============================================================================
# LOGGING
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "processor": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "search": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# =============================================================================
# SILK PROFILING
# =============================================================================

if DEBUG:
    SILKY_AUTHENTICATION = False
    SILKY_AUTHORISATION = False
    SILKY_INTERCEPT_PERCENT = 100
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = False
else:
    SILKY_AUTHENTICATION = True
    SILKY_AUTHORISATION = True
    SILKY_INTERCEPT_PERCENT = 0
    SILKY_PYTHON_PROFILER = False
