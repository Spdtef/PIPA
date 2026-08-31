from abc import ABC, abstractmethod
from typing import AsyncGenerator

class AudioInput(ABC):
    @abstractmethod
    async def start_stream(self) -> AsyncGenerator[bytes, None]:
        pass
        
    @abstractmethod
    async def stop_stream(self):
        pass

class AudioOutput(ABC):
    @abstractmethod
    async def play_stream(self, audio_data_generator: AsyncGenerator[bytes, None]):
        pass
