#!/bin/bash
# Setup script for Voice Feedback Agent
# This script downloads the necessary voice model for the AI to speak.

echo "🎙️ Setting up Voice Feedback Agent..."

# Create voices directory
mkdir -p voices

# Download Piper voice model (English US, Medium quality)
echo "📥 Downloading voice model (en_US-medium)..."
wget -O voices/en_US-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/medium/onnx/model.onnx
wget -O voices/en_US-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/medium/onnx/model.onnx.json

if [ -f "voices/en_US-medium.onnx" ]; then
    echo "✅ Setup complete! Voice model downloaded."
else
    echo "❌ Error: Failed to download voice model. Please check your internet connection."
    exit 1
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Start Ollama: ollama serve"
echo "3. Start the website: streamlit run app.py"
echo "4. Start the AI worker: python worker.py"