from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    memories = relationship("LongTermMemory", back_populates="user")
    conversations = relationship("ConversationMemory", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
