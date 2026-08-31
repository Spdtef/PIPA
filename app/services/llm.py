from google import genai
from sqlalchemy.orm import Session
from app.core.config import settings
from app.memory.conversation import ConversationManager
from app.memory.long_term import LongTermMemoryManager
from app.services.reminders import ReminderEngine
import datetime
import asyncio
import re

class ConversationalLoop:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

    async def process_input(self, db: Session, session_id: str, user_id: int, username: str, user_input: str):
        # 1. Store user message in short-term memory using their actual name
        ConversationManager.add_message(db, session_id, username, user_input, user_id)
        
        # 2. Fetch conversational memory
        recent_history = ConversationManager.get_recent_history(db, session_id, limit=5)
        recent_history.reverse() # Sort chronologically
        
        # Build prompt context
        context_parts = []
        
        # 3. If user_id is set, fetch long term memory
        if user_id:
            try:
                facts = await LongTermMemoryManager.search_facts(db, user_id, user_input, limit=3)
                if facts:
                    context_parts.append("Relevant past facts about the user:")
                    for f in facts:
                        context_parts.append(f"- {f.content}")
            except Exception as e:
                print(f"Skipping semantic search due to error: {e}")
        
        # Build history string
        history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in recent_history])
        
        current_utc = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        system_instruction = (
            "You are Pipa, a warm, highly empathetic, and natural-sounding emotional support buddy. "
            f"The current UTC time is exactly {current_utc}. "
            "You have access to the user's short-term chat history and long-term memory facts. "
            "CRITICAL: Keep your responses EXTREMELY short, conversational, and concise (1-2 sentences max). "
            "Never use bullet points or long explanations. Speak like a real person in a casual voice chat. "
            "If you do not know the user's name, naturally ask for it. When the user tells you their name, output: <IDENTIFY_USER>their name</IDENTIFY_USER>. "
            "You MUST aggressively use <STORE_FACT>fact</STORE_FACT> to remember ANY detail the user mentions about their life, family, pets, belongings, or preferences (e.g. 'User has a famous orange cat named Kattappa', 'User likes water'). "
            "If the user asks to set a reminder, output: <REMINDER>YYYY-MM-DD HH:MM:SS|reminder message</REMINDER> (Use UTC time). "
        )
        
        prompt = f"System: {system_instruction}\n\nContext:\n{chr(10).join(context_parts)}\n\nRecent History:\n{history_str}\n\nAssistant:"

        # Generate response
        if not self.client:
            response_text = "I am a stub because GEMINI_API_KEY is not set."
        else:
            models_to_try = [
                'gemini-3.5-flash-lite',
                'gemini-2.0-flash',
                'gemini-2.0-flash-lite'
            ]
            response_text = None
            for model_name in models_to_try:
                try:
                    from google.genai import types
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            automatic_function_calling={"disable": True}
                        )
                    )
                    response_text = response.text
                    break  # Success!
                except Exception as e:
                    print(f"Model {model_name} failed: {str(e)}")
                    continue
            
            if response_text is None:
                response_text = "Sorry, all models failed to generate a response."
        
        # 4. Extract Identity, Facts, and Reminders, and STRIP the tags completely
        
        # Identity parsing
        id_match = re.search(r"<IDENTIFY_USER>(.*?)</IDENTIFY_USER>", response_text)
        if id_match:
            new_name = id_match.group(1).strip()
            # Lookup or create user
            from app.models.user import User
            from app.models.memory import ConversationMemory
            user = db.query(User).filter(User.username == new_name).first()
            if not user:
                user = User(username=new_name)
                db.add(user)
                db.commit()
                db.refresh(user)
            
            user_id = user.id
            username = user.username
            
            # Retroactively update short-term history for this session with their real name
            db.query(ConversationMemory).filter(
                ConversationMemory.session_id == session_id,
                ConversationMemory.role == "Unknown"
            ).update({"role": username, "user_id": user_id}, synchronize_session=False)
            db.commit()

        # Find all facts
        for fact_match in re.finditer(r"<STORE_FACT>(.*?)</STORE_FACT>", response_text):
            if user_id:
                try:
                    await LongTermMemoryManager.store_fact(db, user_id, fact_match.group(1).strip())
                except Exception as e:
                    print(f"Failed to store fact: {e}")
        
        # Find all reminders
        for rem_match in re.finditer(r"<REMINDER>(.*?)\|(.*?)</REMINDER>", response_text):
            if user_id:
                try:
                    time_str = rem_match.group(1).strip()
                    msg = rem_match.group(2).strip()
                    trigger_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    ReminderEngine.create_reminder(db, user_id, msg, trigger_time)
                except Exception as e:
                    print(f"Failed to set reminder: {e}")
                    
        # CRITICAL: Always strip out ALL tags from the text so the TTS engine doesn't freeze or try to speak them
        response_text = re.sub(r"<IDENTIFY_USER>.*?</IDENTIFY_USER>", "", response_text)
        response_text = re.sub(r"<STORE_FACT>.*?</STORE_FACT>", "", response_text)
        response_text = re.sub(r"<REMINDER>.*?</REMINDER>", "", response_text)
        response_text = response_text.strip()

        # Save assistant message to memory
        ConversationManager.add_message(db, session_id, "Pipa", response_text, user_id)

        return response_text, user_id, username
