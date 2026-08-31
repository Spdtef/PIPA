import asyncio
from sqlalchemy.orm import Session
from app.audio.laptop_io import LaptopAudioInput, LaptopAudioOutput
from app.audio.filtering import AudioFilter
from app.audio.stt import STTEngine
from app.audio.tts import TTSEngine
from app.services.llm import ConversationalLoop
import uuid

class AssistantPipeline:
    def __init__(self, db: Session, username: str = "Unknown"):
        self.audio_in = LaptopAudioInput(chunk=320) # 20ms chunk at 16000Hz (16000 * 0.02 = 320 frames. 1 frame = 2 bytes)
        self.audio_out = LaptopAudioOutput()
        self.vad_filter = AudioFilter(aggressiveness=3, sample_rate=16000)
        self.stt = STTEngine(sample_rate=16000, sample_width=2)
        self.tts = TTSEngine()
        self.llm_loop = ConversationalLoop()
        self.db = db
        self.session_id = str(uuid.uuid4())
        
        self.user_id = None
        self.username = "Unknown"
        
    async def _reminder_callback(self, user_id: int, message: str):
        print(f"\n[REMINDER]: {message}")
        await self.tts.generate_audio(f"Hey! Here is your reminder: {message}")

    async def run(self):
        print("Starting voice assistant pipeline...")
        
        # Start reminder background task
        from app.services.reminders import ReminderEngine
        asyncio.create_task(ReminderEngine.trigger_alerts(self.db, self._reminder_callback))
        
        stream = self.audio_in.start_stream()
        
        is_speaking = False
        speech_buffer = []
        silence_counter = 0
        SILENCE_THRESHOLD = 50 # 50 * 20ms = 1 second of silence to trigger end of speech
        MAX_UTTERANCE_CHUNKS = 750 # 750 * 20ms = 15 seconds max speech duration
        
        print("\n[Listening...]")
        async for chunk in stream:
            # chunk is 640 bytes (320 frames * 2 bytes)
            # check if it contains speech, force cut-off if utterance gets too long
            if self.vad_filter.is_speech(chunk) and len(speech_buffer) < MAX_UTTERANCE_CHUNKS:
                if not is_speaking:
                    is_speaking = True
                speech_buffer.append(chunk)
                silence_counter = 0
            else:
                if is_speaking:
                    speech_buffer.append(chunk)
                    silence_counter += 1
                    if silence_counter > SILENCE_THRESHOLD:
                        # End of utterance
                        is_speaking = False
                        audio_data = b"".join(speech_buffer)
                        speech_buffer = []
                        silence_counter = 0
                        
                        # Transcribe
                        text = await self.stt.transcribe(audio_data)
                        text = self.vad_filter.clean_transcription(text)
                        
                        if text:
                            print(f"\nYou: {text}")
                            
                            # process_input now returns the potentially updated user state
                            response_text, self.user_id, self.username = await self.llm_loop.process_input(
                                self.db, self.session_id, self.user_id, self.username, text
                            )
                            print(f"Pipa: {response_text}")
                            
                            # TTS Processing
                            audio_resp = await self.tts.generate_audio(response_text)
                            
                            if audio_resp:
                                # Play audio (we create a small async generator to pass to play_stream)
                                async def _resp_gen():
                                    # chunk the output for smoother playback if needed, or yield all at once
                                    yield audio_resp
                                
                                await self.audio_out.play_stream(_resp_gen())
                            print("\n[Listening...]")
