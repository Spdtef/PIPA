from fastapi import FastAPI
from app.api.router import api_router
from app.core.database import engine
from app.models.base import Base

from sqlalchemy import text
from sqlalchemy.exc import NotSupportedError, ProgrammingError

try:
    with engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
        conn.commit()
except (NotSupportedError, ProgrammingError) as e:
    print("=" * 80)
    print("CRITICAL WARNING: pgvector extension is not installed on your PostgreSQL server.")
    print("Please install pgvector (https://github.com/pgvector/pgvector) to use memory features.")
    print("The backend will start, but database operations involving embeddings will fail.")
    print("=" * 80)
except Exception as e:
    print(f"WARNING: Could not create vector extension: {e}")

# Create database tables
# In production, use Alembic for migrations
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Could not create tables (likely due to missing pgvector): {e}")

app = FastAPI(title="Voice Assistant API")

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Voice Assistant Backend Running"}
