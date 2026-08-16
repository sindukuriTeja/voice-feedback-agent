"""
Voice Feedback Agent - Local Test
Tests: Microphone -> Whisper -> Ollama -> Piper -> Speaker
"""
import numpy as np
import sounddevice as sd
import ollama
from faster_whisper import WhisperModel
from piper import PiperVoice
import time

# --- Configuration ---
MODEL_SIZE = "small"          # Whisper model size (tiny, base, small, medium)
OLLAMA_MODEL = "qwen3:4b"     # The local AI model
VOICE_PATH = "voices/en_US-medium.onnx"
VOICE_CONFIG = "voices/en_US-medium.onnx.json"

# --- 1. Initialize Components ---
print("🎙️  Loading Whisper (Speech-to-Text)...")
whisper = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

print("🔊  Loading Piper (Text-to-Speech)...")
piper = PiperVoice.load(VOICE_PATH, config_path=VOICE_CONFIG)

print("🧠  Connecting to Ollama (AI Brain)...")
# Check if Ollama is running
try:
    ollama.list()
except Exception:
    print("❌ Error: Ollama is not running! Please run 'ollama serve' in another terminal.")
    exit()

# --- 2. The AI Logic ---
def get_ai_response(user_text):
    """Send text to Ollama and get a short, conversational reply."""
    prompt = f"""You are a friendly customer feedback agent. 
    Keep your response VERY short (1-2 sentences). 
    Speak naturally. Do not use markdown.
    
    User said: "{user_text}"
    
    Your response:"""

    response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

def speak(text):
    """Convert text to speech and play it."""
    print(f"🤖 Agent: {text}")
    audio = piper.synthesize(text)
    sd.play(audio.audio, samplerate=audio.sample_rate)
    sd.wait()

def listen():
    """Record audio from microphone until silence."""
    print("🎤 Listening... (Speak now)")
    
    # Record for 5 seconds or until silence
    duration = 5
    sample_rate = 16000
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    return recording.flatten()

def transcribe(audio):
    """Convert audio to text using Whisper."""
    segments, _ = whisper.transcribe(audio, beam_size=1, language="en")
    return "".join(seg.text for seg in segments).strip()

# --- 3. Main Loop ---
def main():
    speak("Hello! I am your test AI agent. Say 'hello' to start, or 'quit' to stop.")

    while True:
        # 1. Listen
        audio = listen()
        
        # 2. Transcribe
        user_text = transcribe(audio)
        if not user_text:
            continue
            
        print(f"👤 You: {user_text}")
        
        # 3. Exit check
        if user_text.lower() in ["quit", "exit", "stop", "goodbye"]:
            speak("Goodbye! Thanks for testing.")
            break
        
        # 4. AI Response
        reply = get_ai_response(user_text)
        
        # 5. Speak
        speak(reply)
        print("-" * 30)

if __name__ == "__main__":
    main()