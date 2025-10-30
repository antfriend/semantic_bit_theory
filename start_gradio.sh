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
    echo "  python3.13 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install gradio graphviz"
    echo "  pip install -e ./semantic_bit"
    exit 1
fi

# Check if semantic_bit package is installed
if ! "$SCRIPT_DIR/venv/bin/python" -c "import semantic_bit" 2>/dev/null; then
    echo "⚠️  semantic_bit package not installed"
    echo ""
    echo "Installing now..."
    "$SCRIPT_DIR/venv/bin/pip" install -e ./semantic_bit
    echo ""
fi

# Start the app
echo "📊 Opening Gradio at http://localhost:7860"
echo "   Press Ctrl+C to stop the server"
echo ""

"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/semantic_bit/demo/gradio_app.py"
