# Semantic Bit Theory Examples

This directory contains example files demonstrating the semantic-bit CLI functionality.

## Files

- **`sample_text.txt`** - Example input text with multiple sentences
- **`sample_output.json`** - JSON output from encoding the sample text
- **`sample_graph.dot`** - DOT graph generated from the JSON output

## Usage Examples

### Basic Pipeline
```bash
# Encode text to JSON
semantic-bit encode -f sample_text.txt -o output.json

# Decode JSON to DOT graph
semantic-bit decode -f output.json -o graph.dot

# Complete pipeline
semantic-bit encode -f sample_text.txt | semantic-bit decode --name "ExampleGraph"
```

### Visualization
If you have Graphviz installed, you can visualize the graph:
```bash
# Generate PNG image
dot -Tpng sample_graph.dot -o graph.png

# Generate SVG
dot -Tsvg sample_graph.dot -o graph.svg
```

## Expected Output

The sample text contains sentences that work well with the current heuristic-based parser:
- Sentences with auxiliary verbs (is/are/was/were)
- Simple subject-verb-object structures
- Prepositional phrases attached to verbs

Sentences are parsed into Point-Line-Point triples representing the semantic relationships.