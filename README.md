# Pipa: Emotional Support Voice Assistant

## What is Pipa?
Pipa is a warm, highly empathetic, and natural-sounding AI voice assistant designed to act as an emotional support buddy. Unlike robotic and overly verbose assistants, Pipa is engineered to keep responses extremely short (1-2 sentences), conversational, and casual, mimicking a real phone call with a friend. She dynamically learns who you are, aggressively remembers your personal habits and preferences, and can even set real-time background reminders.

## Architecture
Pipa is built on a highly optimized, lightweight Python backend:
- **Core Loop:** Asynchronous pipeline (`asyncio`) managing concurrent listening, thinking, and speaking tasks.
- **Voice Activity Detection (VAD):** `webrtcvad` filters background noise (high aggressiveness) and automatically detects when you start and stop speaking.
- **Speech-to-Text (STT):** Google Web Speech API for fast, free transcription.
- **Text-to-Speech (TTS):** `edge-tts` (using the high-quality `en-US-AriaNeural` voice) played natively through `pygame.mixer` for seamless, non-blocking MP3 output.
- **Networking:** Built with `FastAPI` to support future WebSocket audio streaming for external microcontrollers.

## Hardware
Pipa is completely hardware-agnostic. 
- **Current Setup:** Runs purely on a standard Windows/Linux/Mac laptop using the built-in microphone and speakers.
- **Raspberry Pi Ready:** The architecture is designed so it can be deployed 100% self-contained on a Raspberry Pi (using a USB microphone/speaker). Since the AI processing is handled via cloud APIs, the Pi CPU usage remains extremely low.

## AI Capabilities
Pipa is powered by the **Google Gemini API** (using ultra-fast models like Flash/Flash-Lite). 
To maximize processing speed and prevent the TTS engine from freezing, standard Automatic Function Calling (AFC) is disabled. Instead, Pipa uses a custom pseudo-XML tagging system. She natively outputs tags like `<IDENTIFY_USER>`, `<STORE_FACT>`, and `<REMINDER>` within her text stream. The backend regex engine intercepts, strips, and executes these commands instantly before sending the clean text to the audio speaker.

## Memory Architecture
Pipa features a robust, multi-tiered memory system backed by a local **PostgreSQL** database with the **`pgvector`** extension:
1. **Identity (`users`):** Pipa dynamically asks for your name if she doesn't know you. Once identified, she permanently ties your voice session to your database profile and retroactively links past anonymous messages in the session to your name.
2. **Short-Term Memory (`conversation_memory`):** A rolling window that strictly maintains only the 10 most recent messages to keep the LLM context window cheap and hyper-focused.
3. **Long-Term Memory (`long_term_memory`):** When Pipa detects a personal fact (e.g., "I have a famous cat named Kattappa"), she generates a 768-dimensional mathematical embedding and saves it to the vector database. When you speak to her later, she performs a cosine-similarity search to recall relevant facts seamlessly.
4. **Temporal Memory (`reminders`):** An asynchronous background engine polls the database and interrupts the pipeline to deliver real-time voice alerts.

## Current Prototype
The current prototype runs locally via a continuous command-line loop. It utilizes a `LaptopAudioInput` and `LaptopAudioOutput` interface to grab microphone bytes and play audio through the local OS mixer. 

## How to run it

### 1. Prerequisites
- Python 3.11+
- PostgreSQL (with the [`pgvector`](https://github.com/pgvector/pgvector) extension compiled and installed)
- **Linux/Raspberry Pi users:** You must install audio drivers first: `sudo apt-get install portaudio19-dev python3-pyaudio`

### 2. Installation
```bash
# Clone the repo and enter the directory
git clone <your-repo-url>
cd Pipa

# Create a virtual environment and install dependencies
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/postgres
```

### 4. Initialize the Database
This script will build the tables and apply the vector extensions:
```bash
python init_db.py
```

### 5. Start Pipa
```bash
python run_assistant.py
```

## Roadmap
- **ESP32 Integration:** Transition the local laptop audio interfaces to WebSocket streams (`app/api/endpoints/audio.py`) so a cheap ESP32 with an I2S microphone and speaker can act as the physical hardware interface, while the Raspberry Pi acts purely as a headless backend server.
