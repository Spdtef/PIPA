import pyaudio
import asyncio
from typing import AsyncGenerator
from app.audio.interfaces import AudioInput, AudioOutput

class LaptopAudioInput(AudioInput):
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=16000):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False

    async def start_stream(self) -> AsyncGenerator[bytes, None]:
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        self.is_running = True
        while self.is_running:
            # Using asyncio.to_thread to avoid blocking the event loop
            data = await asyncio.to_thread(self.stream.read, self.chunk, exception_on_overflow=False)
            yield data

    async def stop_stream(self):
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

class LaptopAudioOutput(AudioOutput):
    def __init__(self, format=pyaudio.paInt16, channels=1, rate=16000):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.p = pyaudio.PyAudio()

    async def play_stream(self, audio_data_generator: AsyncGenerator[bytes, None]):
        stream = self.p.open(format=self.format,
                             channels=self.channels,
                             rate=self.rate,
                             output=True)
        try:
            async for data in audio_data_generator:
                await asyncio.to_thread(stream.write, data)
        finally:
            stream.stop_stream()
            stream.close()
            self.p.terminate()
