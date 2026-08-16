"""
FeedbackBot Worker (Cloud Enhanced)
Uses ElevenLabs for Voice and NVIDIA NIM for AI Brain.
Includes sentiment analysis, scoring, and live logging.
"""
import sqlite3
import time
import os
import numpy as np
import sounddevice as sd
import tempfile
import pydub
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# --- Configuration ---
DB_NAME = "feedback_bot.db"

# API Keys
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Models
WHISPER_MODEL_SIZE = "small"
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB" # "Rachel" - Professional female voice
NVIDIA_MODEL = "meta/llama-3.1-8b-instruct" # Smart cloud model

# --- 1. Initialize Components ---
print("🤖 Worker Initializing (Cloud Enhanced)...")

from faster_whisper import WhisperModel
whisper = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

from elevenlabs import ElevenLabs
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

from openai import OpenAI
# NVIDIA NIM uses the OpenAI format but with a custom base URL
nim_client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# --- Helper Functions ---
def add_log(level, message):
    """Add a log entry to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO logs (level, message) VALUES (?, ?)", (level, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Log Error: {e}")

def analyze_sentiment_and_score(text):
    """Use NVIDIA NIM to analyze sentiment and give a score (0-5)."""
    prompt = f"""
    Analyze the following customer feedback. 
    Return ONLY a JSON object with two keys: "sentiment" (Positive/Neutral/Negative) and "score" (0-5).
    
    Feedback: "{text}"
    
    Return JSON only:"""

    try:
        response = nim_client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        import json
        result = json.loads(response.choices[0].message.content.strip())
        return result.get("sentiment", "Neutral"), result.get("score", 3)
    except:
        return "Neutral", 3

# --- 2. The AI Logic ---
def get_ai_response(user_text, script):
    """Send text to NVIDIA NIM and get a short, conversational reply."""
    prompt = f"""You are a friendly customer feedback agent. 
    Your goal is to collect feedback based on this script: "{script}"
    
    Keep your response VERY short (1-2 sentences). 
    Speak naturally. Do not use markdown.
    
    User said: "{user_text}"
    
    Your response:"""

    response = nim_client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def speak(text):
    """Convert text to speech using ElevenLabs and play it."""
    print(f"🤖 AI: {text}")
    add_log("INFO", f"AI Speaking: {text[:50]}...")
    
    # Generate audio from ElevenLabs
    audio = client.generate(
        text=text,
        voice=ELEVENLABS_VOICE_ID,
        model="eleven_multilingual_v2"
    )
    
    # Save to temporary file and play
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        for chunk in audio:
            f.write(chunk)
        temp_path = f.name
    
    # Load MP3 and convert to audio data
    sound = pydub.AudioSegment.from_mp3(temp_path)
    audio_data = np.array(sound.get_array_of_samples(), dtype=np.float32) / 32768.0
    
    sd.play(audio_data, samplerate=sound.frame_rate)
    sd.wait()
    
    os.remove(temp_path)

def listen():
    """Record audio from microphone until silence."""
    print("🎤 Listening... (Speak now)")
    add_log("INFO", "Listening to user...")
    
    # Record for 5 seconds
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
def conduct_interview(user, campaign):
    """Run a full interview with one user."""
    print(f"\n--- Starting Interview with {user['name']} ({user['phone']}) ---")
    add_log("INFO", f"Starting interview with {user['name']}")
    
    speak(f"Hello {user['name']}, this is a quick feedback survey. Do you have a minute?")
    
    questions = ["q1", "q2", "q3"]
    answers = {}
    
    for q in questions:
        # Ask the question based on the script
        speak(f"Next question: {campaign['script']}")
        
        # Listen to user
        audio = listen()
        user_text = transcribe(audio)
        if not user_text:
            continue
        print(f"👤 User: {user_text}")
        add_log("INFO", f"User said: {user_text[:50]}...")
        
        # Save answer
        answers[q] = user_text
        
        # AI acknowledges
        reply = get_ai_response(user_text, "Acknowledge the answer briefly and move to the next point.")
        speak(reply)
        
    # Finalize
    speak("Thank you for your feedback!")
    
    # Analyze sentiment and score
    all_answers = " ".join(answers.values())
    sentiment, score = analyze_sentiment_and_score(all_answers)
    
    # Save to DB
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        INSERT INTO results (user_id, campaign_id, q1, q2, q3, notes, sentiment, score) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user['id'], campaign['id'], answers.get('q1'), answers.get('q2'), answers.get('q3'), 
          "Completed via Cloud AI", sentiment, score))
    
    conn.execute("UPDATE users SET status='Completed' WHERE id=?", (user['id'],))
    conn.commit()
    conn.close()
    
    print(f"✅ Interview with {user['name']} saved to database.")
    add_log("INFO", f"Interview completed with {user['name']} - Score: {score}/5, Sentiment: {sentiment}")

def run_loop():
    """Main loop: Check for active campaigns and pending users."""
    print("🔄 Worker is running. Checking for tasks...")
    add_log("INFO", "Worker started")
    
    while True:
        conn = sqlite3.connect(DB_NAME)
        
        # Find active campaign
        campaign = conn.execute("SELECT * FROM campaigns WHERE status='Active' LIMIT 1").fetchone()
        
        if campaign:
            campaign = dict(zip([col[0] for col in conn.description], campaign))
            
            # Find pending user
            user = conn.execute("SELECT * FROM users WHERE status='Pending' LIMIT 1").fetchone()
            
            if user:
                user = dict(zip([col[0] for col in conn.description], user))
                conduct_interview(user, campaign)
            else:
                print("ℹ️ No pending users for this campaign.")
                add_log("WARNING", "No pending users for active campaign")
                conn.execute("UPDATE campaigns SET status='Completed' WHERE id=?", (campaign['id'],))
                conn.commit()
        else:
            print("ℹ️ No active campaigns. Waiting...")
            add_log("INFO", "No active campaigns. Waiting...")
        
        conn.close()
        time.sleep(10) # Check every 10 seconds

if __name__ == "__main__":
    run_loop()