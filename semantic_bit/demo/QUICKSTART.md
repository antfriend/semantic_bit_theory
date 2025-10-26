# Quick Start - Visual Testing Interface

Get the demo running in 3 minutes!

## Step 1: Install Graphviz (System)

**macOS**:
```bash
brew install graphviz
```

**Ubuntu/Debian**:
```bash
sudo apt-get install graphviz
```

**Windows**:
Download from: https://graphviz.org/download/

## Step 2: Install Python Dependencies

```bash
cd semantic_bit
pip install -r demo/requirements.txt
```

## Step 3: Run!

```bash
./demo/run_demo.sh
```

Or:
```bash
python demo/gradio_app.py
```

## Step 4: Open Browser

Go to: **http://localhost:7860**

## Try It Out!

1. **Enter text**: "The cat is sitting on the mat."
2. **Click**: "🚀 Process Text"
3. **View**: 📊 Graph Visualization tab
4. **See**: Beautiful semantic graph!

---

That's it! The interface is running. See `README.md` for full documentation.
