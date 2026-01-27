#!/bin/bash
# Download Piper TTS model for AADS voice system

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

MODELS_DIR="./models/piper"
MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
MODEL_FILE="$MODELS_DIR/en_US-lessac-medium.onnx"

echo "Piper TTS Model Download"
echo "========================"
echo ""

if [ ! -d "$MODELS_DIR" ]; then
    echo "Creating models directory: $MODELS_DIR"
    mkdir -p "$MODELS_DIR"
fi

if [ -f "$MODEL_FILE" ]; then
    echo "Model already exists: $MODEL_FILE"
    ls -lh "$MODEL_FILE"
    echo ""
    echo "Piper TTS model is ready."
    exit 0
fi

echo "Downloading Piper TTS model..."
echo "URL: $MODEL_URL"
echo ""

if command -v curl >/dev/null 2>&1; then
    curl -L -o "$MODEL_FILE" "$MODEL_URL" --progress-bar
elif command -v wget >/dev/null 2>&1; then
    wget -O "$MODEL_FILE" "$MODEL_URL"
else
    echo "Neither curl nor wget found. Please install one of them."
    exit 1
fi

if [ -f "$MODEL_FILE" ]; then
    FILE_SIZE=$(du -h "$MODEL_FILE" | cut -f1)
    echo ""
    echo "Model downloaded successfully."
    echo "File: $MODEL_FILE"
    echo "Size: $FILE_SIZE"
    echo ""
    echo "Piper TTS is ready for voice synthesis."
else
    echo "Download failed."
    exit 1
fi
