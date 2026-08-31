import webrtcvad

class AudioFilter:
    def __init__(self, aggressiveness=3, sample_rate=16000):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        
    def is_speech(self, audio_frame: bytes) -> bool:
        # frame length must be 10, 20, or 30 ms
        try:
            return self.vad.is_speech(audio_frame, self.sample_rate)
        except Exception:
            return False

    def clean_transcription(self, text: str) -> str:
        # Basic cleanup
        return text.strip()
