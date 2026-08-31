from app.core.database import engine
from app.models.base import Base
from app.models.user import User
from app.models.memory import ConversationMemory, LongTermMemory
from app.models.reminder import Reminder
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, NotSupportedError

def init_db():
    print("Dropping tables...")
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS long_term_memory CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS conversation_memory CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS reminders CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    except Exception as e:
        print(f"Error dropping: {e}")

    print("Creating tables...")
    try:
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
            conn.commit()
    except (NotSupportedError, ProgrammingError) as e:
        print("pgvector not found. LongTermMemory table creation will fail.")
    except Exception as e:
        print(f"Error checking pgvector: {e}")

    try:
        User.__table__.create(engine)
        print("Created User table.")
    except Exception as e:
        print(f"Error creating User table: {e}")

    try:
        ConversationMemory.__table__.create(engine)
        print("Created ConversationMemory table.")
    except Exception as e:
        print(f"Error creating ConversationMemory table: {e}")
        
    try:
        Reminder.__table__.create(engine)
        print("Created Reminder table.")
    except Exception as e:
        print(f"Error creating Reminder table: {e}")

    try:
        LongTermMemory.__table__.create(engine)
        print("Created LongTermMemory table.")
    except Exception as e:
        print(f"Error creating LongTermMemory table: {e}")

if __name__ == "__main__":
    init_db()
