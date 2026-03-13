#!/bin/bash
# BabelBot - Quick Setup Script
# Run this first: chmod +x setup.sh && ./setup.sh

echo "=== BabelBot Setup ==="

# Install Python dependencies
echo "[1/3] Installing Python packages..."
pip install -r requirements.txt

# Check for pyaudio system dependency
echo "[2/3] Checking system dependencies..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew install portaudio ffmpeg 2>/dev/null || echo "brew packages may already be installed"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo apt-get install -y portaudio19-dev ffmpeg 2>/dev/null || echo "apt packages may already be installed"
fi

# Prompt for API keys
echo "[3/3] Setting up API keys..."
echo ""
echo "Set these environment variables before running:"
echo ""
echo '  export SMALLEST_API_KEY="your-key-from-console.smallest.ai"'
echo '  # Ollama runs locally — no API key needed (ensure ollama is running)'
echo '  export CYBERWAVE_API_KEY="your-cyberwave-key"'
echo ""
echo "=== Setup Complete ==="
echo ""
echo "To test without robot:  python main.py --test"
echo "To run with mic:        python main.py"
