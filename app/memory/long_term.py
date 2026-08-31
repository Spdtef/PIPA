from sqlalchemy.orm import Session
from app.models.memory import LongTermMemory
from app.memory.embeddings import generate_embedding

class LongTermMemoryManager:
    @staticmethod
    async def store_fact(db: Session, user_id: int, content: str):
        # Prevent exact duplicate facts from polluting the memory
        existing = db.query(LongTermMemory).filter(
            LongTermMemory.user_id == user_id,
            LongTermMemory.content == content
        ).first()
        if existing:
            return existing
            
        embedding = await generate_embedding(content)
        memory = LongTermMemory(
            user_id=user_id,
            content=content,
            embedding=embedding
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    async def search_facts(db: Session, user_id: int, query: str, limit: int = 3):
        query_embedding = await generate_embedding(query)
        # Using pgvector <=> operator for cosine distance
        results = db.query(LongTermMemory).filter(
            LongTermMemory.user_id == user_id
        ).order_by(
            LongTermMemory.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
        return results
