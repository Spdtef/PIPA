from sqlalchemy.orm import Session
from app.models.memory import ConversationMemory

class ConversationManager:
    @staticmethod
    def add_message(db: Session, session_id: str, role: str, content: str, user_id: int = None):
        msg = ConversationMemory(
            session_id=session_id,
            role=role,
            content=content,
            user_id=user_id
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        
        # Prune old messages to only keep the last 10 for this session
        # This keeps the database lightweight and only stores relevant context
        recent_ids = [row[0] for row in db.query(ConversationMemory.id).filter(
            ConversationMemory.session_id == session_id
        ).order_by(ConversationMemory.timestamp.desc()).limit(10).all()]
        
        if recent_ids:
            db.query(ConversationMemory).filter(
                ConversationMemory.session_id == session_id,
                ConversationMemory.id.not_in(recent_ids)
            ).delete(synchronize_session=False)
            db.commit()
        
        return msg

    @staticmethod
    def get_recent_history(db: Session, session_id: str, limit: int = 10):
        return db.query(ConversationMemory).filter(
            ConversationMemory.session_id == session_id
        ).order_by(ConversationMemory.timestamp.desc()).limit(limit).all()
