import edge_tts
import asyncio
import tempfile
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import uuid

class TTSEngine:
    def __init__(self, voice="en-US-AriaNeural"):
        self.voice = voice
        pygame.mixer.init()
        
    async def generate_audio(self, text: str) -> bytes:
        unique_id = uuid.uuid4().hex
        temp_path = os.path.join(tempfile.gettempdir(), f'tts_output_{unique_id}.mp3')
        
        # Generate high-quality natural voice using edge-tts
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(temp_path)
        
        # Play directly using pygame to handle MP3 natively
        def _play():
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            try:
                os.remove(temp_path)
            except:
                pass
                
        await asyncio.to_thread(_play)
        
        # Return empty bytes so the pipeline doesn't try to play it again with PyAudio
        return b""
