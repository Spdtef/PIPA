import asyncio
from app.core.database import SessionLocal
from app.audio.pipeline import AssistantPipeline
import logging

# Set up simple logging filter to ignore annoying warning from pywin32 if any
logging.getLogger("comtypes").setLevel(logging.INFO)

async def main():
    db = SessionLocal()
    print("========================================")
    print(" Welcome to Pipa! ")
    print("========================================")
    
    try:
        pipeline = AssistantPipeline(db)
        await pipeline.run()
    except KeyboardInterrupt:
        print("\nStopping assistant...")
    except Exception as e:
        print(f"\nError running assistant: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
