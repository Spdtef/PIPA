import speech_recognition as sr
import asyncio
import io
import wave

class STTEngine:
    def __init__(self, sample_rate=16000, sample_width=2):
        self.recognizer = sr.Recognizer()
        self.sample_rate = sample_rate
        self.sample_width = sample_width

    async def transcribe(self, audio_data: bytes) -> str:
        # Convert raw bytes to a format speech_recognition understands
        # We need to wrap it in a WAV container in memory
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data)
        
        wav_io.seek(0)
        
        def _recognize():
            with sr.AudioFile(wav_io) as source:
                audio = self.recognizer.record(source)
            try:
                # Using Google's free Web Speech API
                return self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                print(f"Could not request results from STT service; {e}")
                return ""
                
        return await asyncio.to_thread(_recognize)
