from google import genai
from app.core.config import settings
import asyncio

client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

async def generate_embedding(text: str) -> list[float]:
    # If API key is not set, return dummy data for testing
    if not client:
        return [0.0] * 768
        
    from google.genai import types
    models_to_try = ['gemini-embedding-2', 'gemini-embedding-001']
    for model_name in models_to_try:
        try:
            # run in thread pool to prevent blocking the async loop
            result = await asyncio.to_thread(
                client.models.embed_content,
                model=model_name,
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            return result.embeddings[0].values
        except Exception as e:
            last_error = e
            continue
            
    print(f"Embedding failed completely: {last_error}")
    # Return zero vector so it doesn't crash the pipeline, though semantic search won't work well for this specific fact
    return [0.0] * 768
