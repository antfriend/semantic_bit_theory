#!/bin/bash

# Launcher script for Semantic Bit Theory v2.0 Visual Testing Interface
# Makes it easy to start the demo from anywhere

cd "$(dirname "$0")"

echo "🎨 Semantic Bit Theory v2.0 - Visual Testing Interface"
echo "=================================================="
echo ""

# Check if dependencies are installed
if ! python3 -c "import gradio" 2>/dev/null; then
    echo "❌ Gradio is not installed!"
    echo ""
    echo "Install with:"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

if ! python3 -c "import graphviz" 2>/dev/null; then
    echo "⚠️  Warning: Python graphviz package not installed"
    echo "   Graph visualization may not work"
    echo ""
fi

# Check if system graphviz is installed
if ! command -v dot &> /dev/null; then
    echo "⚠️  Warning: System graphviz not installed"
    echo ""
    echo "Install with:"
    echo "  macOS:    brew install graphviz"
    echo "  Ubuntu:   sudo apt-get install graphviz"
    echo "  Windows:  https://graphviz.org/download/"
    echo ""
fi

echo "🚀 Starting demo..."
echo "📊 Graph visualization is the priority feature!"
echo ""
echo "The interface will open at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 gradio_app.py
