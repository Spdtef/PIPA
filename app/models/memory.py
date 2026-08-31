from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base
import datetime

class ConversationMemory(Base):
    __tablename__ = 'conversation_memory'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String, index=True)
    role = Column(String) # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")

class LongTermMemory(Base):
    __tablename__ = 'long_term_memory'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="memories")
