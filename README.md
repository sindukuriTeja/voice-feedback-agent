# 🎙️ FeedbackBot Pro

A complete, professional AI-powered voice feedback collection system. Built with Streamlit, ElevenLabs, NVIDIA NIM, and Faster-Whisper.

## 📂 Project Structure

```
voice-feedback-agent/
├── app.py              # Professional Web Dashboard (8 Pages)
├── worker.py           # Cloud AI Engine (ElevenLabs + NVIDIA NIM)
├── .env                # Secure API Keys (ElevenLabs & NVIDIA)
├── requirements.txt    # All Python Dependencies
├── setup.sh            # One-Click Setup Script
└── README.md           # This File
```

## 🚀 How to Run

### Step 1: Install Dependencies
```bash
cd /opt/sandbox/workspace/voice-feedback-agent
pip install -r requirements.txt
```

### Step 2: Run Setup (One-time)
```bash
bash setup.sh
```

### Step 3: Start the Website Dashboard
```bash
streamlit run app.py
```
Open the link shown (e.g., `http://localhost:8501`) in your browser.

### Step 4: Start the AI Worker
```bash
python worker.py
```
*(This connects to your API keys and starts listening to your microphone)*

## 📝 How to Use

1. **Add Users:** Go to "Users" tab → Add manually or upload a CSV file
2. **Create Campaign:** Go to "Campaigns" tab → Write your script and start
3. **Monitor:** Go to "Live Monitor" tab → Watch the AI work in real-time
4. **View Results:** Go to "Results" tab → See answers, scores, and sentiments
5. **Analyze:** Go to "Analytics" tab → See visual charts and trends
6. **Export:** Download results as CSV from the "Results" tab

## 🛠️ Tech Stack

- **Website:** Streamlit (Python)
- **Database:** SQLite
- **AI Brain:** NVIDIA NIM (Llama 3.1 8B)
- **Speech-to-Text:** Faster-Whisper (Local)
- **Text-to-Speech:** ElevenLabs (Cloud)
- **Audio:** SoundDevice & Pydub
- **Analytics:** Plotly

## ⚠️ Notes

- Make sure your microphone and speakers are working.
- The AI uses your internet connection to access ElevenLabs and NVIDIA NIM.
- Your API keys are securely stored in the `.env` file.
- The worker checks for active campaigns every 10 seconds.