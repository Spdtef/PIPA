from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.llm import ConversationalLoop
import uuid
import json

router = APIRouter()
loop = ConversationalLoop()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int = None, db: Session = Depends(get_db)):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    # In a real scenario, we might receive audio stream here
    # and pipe it through our audio filtering and VAD to STT.
    # For testing without audio hardware, we expect text data over the websocket.
    while True:
        try:
            data = await websocket.receive_text()
            # If the user sends a JSON with user_id, we can parse it for testing purposes
            try:
                payload = json.loads(data)
                text = payload.get("text", "")
                uid = payload.get("user_id", user_id)
            except json.JSONDecodeError:
                text = data
            username = payload.get("username", "Unknown") if isinstance(data, str) and "username" in data else "Unknown" # basic fallback

            response, uid, username = await loop.process_input(db, session_id, uid, username, text)
            await websocket.send_text(response)
        except Exception as e:
            print(f"WebSocket disconnected or error: {e}")
            break
