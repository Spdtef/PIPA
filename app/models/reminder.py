from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    trigger_time = Column(DateTime, nullable=False)
    is_triggered = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="reminders")
