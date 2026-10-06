"""Application configuration.

Environment variables are intentionally aligned with the deployment contract.
Security-sensitive values must be supplied by the deployment environment.
"""

import os


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


DATABASE_URL = _env("DATABASE_URL")
ENVIRONMENT = _env("ENVIRONMENT", "development")
SECRET_KEY = _env("SECRET_KEY")
CORS_ORIGINS = [
    origin.strip()
    for origin in _env("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

LEGAL_CORPUS_VERSION = _env("LEGAL_CORPUS_VERSION", "0.1.0")
PRECEDENT_CORPUS_VERSION = _env("PRECEDENT_CORPUS_VERSION", "0.1.0")
ENGINE_VERSION = _env("ENGINE_VERSION", "0.1.0")
