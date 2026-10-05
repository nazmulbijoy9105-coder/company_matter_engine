import os

DATABASE_URL = os.environ.get("CME_DATABASE_URL", "")   # empty => in-memory MVP stores
ENVIRONMENT = os.environ.get("CME_ENV", "dev")
