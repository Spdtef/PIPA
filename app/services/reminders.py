import asyncio
from sqlalchemy.orm import Session
from app.models.reminder import Reminder
import datetime

class ReminderEngine:
    @staticmethod
    def create_reminder(db: Session, user_id: int, message: str, trigger_time: datetime.datetime):
        reminder = Reminder(
            user_id=user_id,
            message=message,
            trigger_time=trigger_time
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    async def trigger_alerts(db: Session, callback):
        # Background task that polls for due reminders
        while True:
            now = datetime.datetime.utcnow()
            due_reminders = db.query(Reminder).filter(
                Reminder.is_triggered == False,
                Reminder.trigger_time <= now
            ).all()
            
            for reminder in due_reminders:
                # Trigger action
                await callback(reminder.user_id, reminder.message)
                db.delete(reminder)
                db.commit()
            await asyncio.sleep(5) # Poll every 5 seconds
