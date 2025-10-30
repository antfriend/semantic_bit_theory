#!/bin/bash
# Convenience script to start the Gradio app
# Usage: ./start_gradio.sh

set -e

# Get script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting Semantic Bit Theory Gradio App..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found at: venv/"
    echo ""
    echo "Please run setup first:"
    echo "  python3 -m venv venv           # Use python3 or python depending on your system"
    echo "  source venv/bin/activate"
    echo "  pip install gradio graphviz"
    echo "  pip install -e ./semantic_bit"
    exit 1
fi

# Check if required packages are installed
MISSING_DEPS=""

if ! "$SCRIPT_DIR/venv/bin/python" -c "import gradio" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS gradio"
fi

if ! "$SCRIPT_DIR/venv/bin/python" -c "import graphviz" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS graphviz"
fi

if ! "$SCRIPT_DIR/venv/bin/python" -c "import semantic_bit" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS semantic_bit"
fi

if [ -n "$MISSING_DEPS" ]; then
    echo "⚠️  Missing dependencies:$MISSING_DEPS"
    echo ""
    echo "Installing now..."

    if [[ "$MISSING_DEPS" == *"gradio"* ]] || [[ "$MISSING_DEPS" == *"graphviz"* ]]; then
        "$SCRIPT_DIR/venv/bin/pip" install gradio graphviz
    fi

    if [[ "$MISSING_DEPS" == *"semantic_bit"* ]]; then
        "$SCRIPT_DIR/venv/bin/pip" install -e ./semantic_bit
    fi

    echo ""
    echo "✅ Dependencies installed"
    echo ""
fi

# Start the app
echo "📊 Opening Gradio at http://localhost:7860"
echo "   Press Ctrl+C to stop the server"
echo ""

"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/semantic_bit/demo/gradio_app.py"
