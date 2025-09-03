# semantic_bit_theory
## Home of the Semantic Bit

### 📈 Semantic Story Encoding and Decoding

Semantic Bit Theory encodes and decodes time-spanning events into a symbolic taxonomy of what it all means. 🌎 🌠 🍄

### It means what you think it means, if you know what I mean.

In Semantic Bit Theory the taxonomic principle of division is:   
- noun or a verb
- object or a predicate
- particle or a wave
- person or a feeling that person is having   
o_o


<img src="./sbt_121.png">   
### "You keep saying that word. I don't think it means what you think it means." -- Princess Bride
<img src="./sbt_17.png">    
<img src="./sbt_1.png">   
<img src="./sbt_19.png">   
<img src="./sbt_23.png">   
<img src="./sbt_5.png">   
<img src="./sbt_103.png"> 
 
## Schema + Examples
- Schema: `schema/semantic-bit.schema.json`
- Valid instances: `examples/alice-bob.json`, `examples/market.json`
- Invalid instance (for testing): `examples/invalid/invalid-bit.json`

Validate with any JSON Schema Draft-07 validator. Examples:
- Node (ajv-cli): `npx ajv validate -s schema/semantic-bit.schema.json -d examples/*.json`
- Python (jsonschema):
  - `python -c "import json,sys,jsonschema; s=json.load(open('schema/semantic-bit.schema.json'));\nimport glob;\n[jsonschema.validate(json.load(open(p)), s) for p in glob.glob('examples/*.json')];\nprint('ok')"`

Or use the included friendly validator (falls back if `jsonschema` is not installed):
- `python tools/validate.py`  
  Validates `examples/*.json` and `examples/invalid/*.json` and prints per-file results.
- Validate custom paths: `python tools/validate.py examples/*.json` 

## CI
- GitHub Actions workflow: `.github/workflows/validate.yml`
- On each push/PR it:
  - Installs Python and `jsonschema`.
  - Validates all valid examples: `python tools/validate.py examples/*.json`.
  - Ensures invalid examples fail validation (job fails if they don’t).

## Pre-commit Hook
- Config: `.pre-commit-config.yaml`
- Installs a local hook that runs `python tools/validate.py` on staged JSON files under `examples/` (excluding `examples/invalid/`).

Setup:
- `pip install pre-commit`
- `pre-commit install`
- Optional one-time run on entire repo: `pre-commit run --all-files`

Notes:
- The hook installs `jsonschema` in its own environment for full validation.
- Invalid examples are excluded from the hook but enforced by CI.

Both example files reference the schema via `$schema` and demonstrate:
- Person/feeling wave state updated by a particle event (`examples/alice-bob.json`).
- Market wave trend terminated by a particle crash (`examples/market.json`).


## Goal: 
Encode and decode time-spanning events into a compact, symbolic system that captures “what it all means” as stories evolve.

## Core unit (“semantic bit”): 
A minimal piece of meaning that situates something in a story along simple, universal semantic splits.

## Scope: 
Semantic encoding, representations, and narratives over time.
Dual Axes (Taxonomic Splits)

- Noun vs Verb: Entities/things vs actions/relations.
- Object vs Predicate: The “thing” vs the statement/property about it.
- Particle vs Wave: Discrete item vs extended, evolving state across time.
- Person vs Feeling: A subject/agent vs the internal state that subject experiences.


## How It Works (Intuition)

- Bits as roles: Each semantic bit places a piece of information on one side of a split (e.g., noun vs verb) to clarify its role in meaning.
- Compositionality: Bits combine into higher-level structures—events, arcs, then stories—preserving who did what, to whom, with what state, over time.
- Time encoding: “Wave-like” bits track persistence and change (e.g., moods, intentions), while “particle-like” bits mark discrete events.

## Simple Example

“Alice loves Bob on Monday.”
Noun/Object: Alice, Bob
Verb/Predicate: loves
Particle: the Monday event of expressing love
Wave: the ongoing state of love across days
Person vs Feeling: Alice (person) having love (feeling)

## Why These Splits Help

- Clarity: Forces each piece of data into a crisp role, reducing ambiguity.
- Portability: Simple, universal distinctions travel well across domains.
- Narrative fit: Cleanly models both snapshots (events) and continuities (states).

## Positioning

Compared to logic/graphs: Like subject–predicate graphs and event schemas, but organized explicitly around a few stable semantic axes.
Use cases: Story understanding, event logging, knowledge graphs, affective computing—anywhere meaning evolves over time.

## Why this helps

### Disambiguation:    
Each token is forced into crisp roles along the splits, reducing ambiguity.
### Time-awareness:    
Particle vs wave keeps events and states distinct but connected.
### Human-centric:    
Person vs feeling captures inner state alongside action, improving narrative fidelity.