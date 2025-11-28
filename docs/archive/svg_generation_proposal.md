**Overview**
- Goal: Add a first-class method to generate an animated SVG that displays all sentences produced by Semantic Bit Theory (SBT), styled by roles (Point vs Line) and animated based on Line→function mappings. The SVG should start focused on the first sentence and auto-transition after 3 seconds. Always append a final sentence: "The End.".

**Key Requirements**
- Include all sentences in order, plus a final "The End." sentence.
- Style roles:
  - Point terms: bold text with white background.
  - Line terms: bold text with green background.
- Map Line terms to built-in animation functions to drive transitions.
- Initial viewport focuses the first sentence; after 3 seconds, transition occurs based on that sentence’s Line mapping.
- Output a single self-contained SVG (inline CSS + minimal inline JS).

**Proposed API**
- New module: `semantic_bit/src/semantic_bit/svg.py:1`
- New function: `def encode_sb_to_animated_svg(sb_json: Dict[str, Any], *, width: int = 1024, height: int = 768, theme: Optional[Dict[str, str]] = None, autoplay: bool = True, interval_ms: int = 3000) -> str`
  - Input: an SBT JSON (v2.0) produced by `encode_text_to_sb` and optionally enriched via `map_functions_to_lines`.
  - Output: an SVG string (caller can write it to a file). A helper `write_svg(svg: str, path: Union[str, Path]) -> Path` may be included for convenience.
- Convenience overload: `def text_to_animated_svg(text: str, functions: Optional[List[Dict[str, str]]] = None, **opts) -> str` that calls `encode_text_to_sb`, `map_functions_to_lines` (if provided), appends "The End.", then renders.
- Export in `semantic_bit/src/semantic_bit/__init__.py:1` for public API.

**Data Flow**
- Caller → `encode_text_to_sb(text)` → SBT JSON
- Optional: `map_assets_to_points` and `map_functions_to_lines` (already provided)
- Ensure final sentence "The End." is appended if not present
- `encode_sb_to_animated_svg(sb_json, ...)` → SVG string

**Sentence Model (v2.0)**
- Patterns include: `triple`, `point-line`, `line-point`, `point-point`, `line`, `point`.
- Rendering extracts Point(s) and Line(s) per sentence:
  - triple: `point1`, `line1`, `point2`
  - point-line: `point`, `line`
  - line-point: `line`, `point`
  - point-point: `point1`, `point2`
  - line: `content`
  - point: `content`

**Rendering Approach**
- One `<g class="sb-sentence" id="sent-<idx>">` per sentence.
- Inside, lay out tokens role-wise as grouped label blocks: `<g class="sb-token sb-point">` and `<g class="sb-token sb-line">`, each containing a `<rect class="bg"/>` and `<text class="label"/>`.
- Position sentences in a vertical list with spacing (e.g., 120px height per row). Compute per-sentence X layout as `[Point] → [Line] → [Point]` with configurable spacing.
- Use a monospace font for predictable layout; onload JS adjusts each background `<rect>` to match text bounding box with padding via `getBBox()`.

**Styling**
- Inline CSS (scoped to SVG):
  - `.sb-point .label { font-weight: 700; fill: #111; }`
  - `.sb-point .bg { fill: #fff; stroke: #333; }`
  - `.sb-line .label { font-weight: 700; fill: #0b3; }`
  - `.sb-line .bg { fill: #c7f7d4; stroke: #0b3; }`
  - Sentence container spacing, arrow `→` glyphs, and focus outline styles.

**Viewport and Focus**
- Root SVG has `viewBox` sized to a single sentence row.
- Add a hidden `<g id="viewport-origin">` reference for smooth panning.
- JS computes each sentence group’s bounding box and sets the initial `viewBox` to "first sentence" bounds (with padding) on load.

**Animation Model**
- Built-in animations driven by function names found on the first applicable Line per sentence. Proposed built-ins:
  - `pan_right`: Pan horizontally across the current sentence.
  - `pan_down`: Pan downward toward the next sentence.
  - `zoom_in`: Zoom into the Line term block.
  - `pulse`: Brief scale/opacity pulse on the Line block.
  - `rotate`: Subtle rotate on the Line block (with transform-origin at center).
  - `fade_to_next`: Fade out current sentence group and focus next.
- Default if unrecognized or absent: `pan_down`.
- Execution order per sentence:
  1) Focus current sentence (set `viewBox` to its bounds)
  2) After `interval_ms` (default 3000), trigger mapped animation
  3) Then move focus to next sentence and repeat
  4) After the last real sentence, append and display the final "The End." sentence with a `fade_to_next` or `zoom_in` effect, then stop.

**Line→Function Mapping**
- Re-use existing enrichment `map_functions_to_lines` output: a Line may have `functions: [{"name": str, "description": str}, ...]`.
- Choose the first recognized `name` to determine animation; fall back to description matching.
- Example recognized names: `pan_right`, `pan_down`, `zoom_in`, `pulse`, `rotate`, `fade_to_next`.

**Minimal Inline JS**
- Responsibilities:
  - Onload, measure `<text>` via `getBBox()` and size/position `<rect.bg>` with padding.
  - Compute and store per-sentence bounding boxes.
  - Initialize viewBox to the first sentence.
  - Autoplay loop every `interval_ms` triggering the chosen effect class on the sentence or its Line token.
  - Transition to next sentence after the effect completes (CSS `transitionend` or timed fallback).
- No external dependencies; limited to DOM APIs supported by inline SVG in browsers.

**CSS Animations**
- Define animation classes for each built-in, e.g.:
  - `.anim-pan-right { transition: transform 800ms ease; transform: translateX(60px); }`
  - `.anim-pan-down { transition: transform 800ms ease; transform: translateY(60px); }`
  - `.anim-zoom-in { animation: zoomIn 800ms ease; } @keyframes zoomIn { from { transform: scale(1); } to { transform: scale(1.2); } }`
  - `.anim-pulse { animation: pulse 800ms ease; } @keyframes pulse { 0%{opacity:1} 50%{opacity:.4} 100%{opacity:1} }`
  - `.anim-rotate { animation: rotate 1000ms ease; } @keyframes rotate { from{transform:rotate(0)} to{transform:rotate(8deg)} }`
  - `.anim-fade-to-next { animation: fade 600ms ease; } @keyframes fade { from{opacity:1} to{opacity:0} }`

**Layout Details**
- Row metrics: `rowHeight=120`, `tokenGap=16`, padding around text `px=8`.
- Token order by pattern type, emitting arrow `→` `text` nodes between role blocks when both are present.
- Each token group gets a stable `id` for JS targeting, e.g., `sent-2-line`.

**Appending "The End."**
- If the last `sentences[-1].original_text` is not exactly `"The End."`, append a synthetic sentence with type `point` and content `"The End."`.

**Error Handling**
- Empty input → create a single sentence: `"The End."` only.
- Non-conforming structures are ignored gracefully; only `content` strings render.
- Text escaping handled for XML entities.

**Testing Strategy**
- Unit tests validate:
  - SVG output is non-empty and contains per-sentence groups and role classes.
  - Background rects exist and JS sizing hook attributes are present.
  - When functions are supplied, recognized class names are present on the relevant sentence group or Line token.
  - The final sentence "The End." is always present and last.
- Golden file snapshot for a small fixture input to catch regressions.

**Example Usage**
- Python:
  - `sb = encode_text_to_sb("The cat sits on the mat. What is a cactus?")`
  - `sb = map_functions_to_lines(sb, [{"name":"zoom_in","description":"zooms"},{"name":"pan_down","description":"pans"}])`
  - `svg = encode_sb_to_animated_svg(sb, width=800, height=600)`
  - `Path("out.svg").write_text(svg, encoding="utf-8")`

**Implementation Plan**
- Add `svg.py` with helpers:
  - `build_sentence_tokens(sentence) -> List[TokenSpec]`
  - `render_svg(sb_json, width, height, theme, interval_ms, autoplay) -> str`
  - `apply_animation_mapping(sentence) -> str` (returns animation key)
- Export new API in `__init__.py`.
- Add a small example script under `examples/` to demonstrate writing a file.
- Add tests in `semantic_bit/tests/` that exercise the above.

**Notes and Tradeoffs**
- Background sizing in pure SVG is awkward; using inline JS for bbox measurement yields accurate padding without heavy dependencies.
- SMIL is unevenly supported; CSS transforms + JS class toggles are more portable.
- The SVG remains a single file, viewable in modern browsers without external assets.

**Timeline**
- Day 1: Implement `svg.py` rendering + background sizing + basic animations.
- Day 2: Wire function mapping, sequencing, and finalize API; add tests and example.
- Day 3: Polish styles, docs, and edge-case handling.

