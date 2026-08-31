#!/bin/bash
echo "=========================================="
echo "    Pipa Setup & Runner (Raspberry Pi)    "
echo "=========================================="

echo "[1/4] Installing Linux Audio Drivers..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio python3-venv

echo "[2/4] Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "[3/4] Installing Python Dependencies..."
pip install -r requirements.txt

echo "[4/4] Launching Pipa..."
python3 run_assistant.py
