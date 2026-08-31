from app.audio.interfaces import AudioInput, AudioOutput
from typing import AsyncGenerator

class ESP32AudioInput(AudioInput):
    # Stub for WebSockets/HTTP I2S streaming from ESP32
    async def start_stream(self) -> AsyncGenerator[bytes, None]:
        pass
        
    async def stop_stream(self):
        pass

class ESP32AudioOutput(AudioOutput):
    async def play_stream(self, audio_data_generator: AsyncGenerator[bytes, None]):
        pass
