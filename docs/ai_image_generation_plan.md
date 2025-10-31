# AI Image Generation - Implementation Plan
**Date**: 2025-10-30
**Status**: Planning Phase
**Budget**: $10/month (expandable later)
**Priority**: Plan now, implement later

---

## Budget Constraints & Strategy

### User Requirements
- ✅ **Budget**: $10/month initially
- ✅ **Preference**: Local/free solutions strongly preferred
- ✅ **Default**: Image generation OFF (user must opt-in)
- ✅ **Monitoring**: Token usage/cost tracking dashboard required
- ✅ **Control**: Toggle button with link to monitoring page

### Strategic Approach
**Primary**: Local Stable Diffusion (FREE)
**Secondary**: API fallback for users without local GPU (paid, with strict limits)

---

## Solution Architecture

### Tier 1: Local Generation (FREE - Recommended)
**What**: Run Stable Diffusion locally on user's machine
**Cost**: $0
**Quality**: High (comparable to DALL-E)
**Speed**: Fast (if GPU available)

**Requirements**:
- GPU with 4GB+ VRAM (NVIDIA preferred)
- ~10GB disk space for models
- Python packages: `diffusers`, `transformers`, `torch`

**Pros**:
- ✅ Zero API costs
- ✅ Unlimited generations
- ✅ Privacy (local processing)
- ✅ Customizable models

**Cons**:
- ⚠️ Requires GPU (or slow on CPU)
- ⚠️ Setup complexity
- ⚠️ Large model downloads

**Implementation**:
```python
# Using Hugging Face Diffusers (free, local)
from diffusers import StableDiffusionPipeline
import torch

# One-time setup (downloads ~4GB model)
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")  # or "cpu" if no GPU

# Generate image from prompt (FREE)
image = pipe(
    "A cat sitting on a mat, digital art style",
    num_inference_steps=50
).images[0]
```

**Estimated Performance**:
- GPU (RTX 3060): ~5-10 seconds per image
- CPU: ~2-5 minutes per image
- Quality: Excellent

### Tier 2: Cloud API with Budget Controls (PAID)
**What**: Use external APIs for users without GPU
**Cost**: ~$0.02-0.04 per image (strict limits)
**Quality**: Excellent
**Speed**: 5-15 seconds

**API Options**:

#### Option A: OpenAI DALL-E 3 (Highest Quality)
- **Cost**: $0.040 per 1024x1024 image
- **Budget impact**: 250 images/month = $10
- **Pros**: Best quality, reliable
- **Cons**: Most expensive

#### Option B: Stability AI (Good Balance)
- **Cost**: $0.02 per image (with API credits)
- **Budget impact**: 500 images/month = $10
- **Pros**: Good quality, reasonable cost
- **Cons**: Requires account

#### Option C: Together.ai (Cheapest)
- **Cost**: ~$0.001-0.005 per image
- **Budget impact**: 2000-10000 images/month = $10
- **Pros**: Very cheap, many models
- **Cons**: Variable quality

**Recommendation**: Together.ai for budget users, with strict rate limits

### Tier 3: Hybrid Approach (BEST)
**What**: Auto-detect GPU and choose method
**Cost**: $0 (local) or controlled (API)

**Logic**:
```python
def generate_image(prompt, use_local=True):
    if use_local and has_gpu():
        # Use local Stable Diffusion (FREE)
        return generate_local(prompt)
    else:
        # Check budget remaining
        if check_budget_available():
            # Use API with cost tracking
            return generate_api(prompt)
        else:
            # Budget exceeded
            return show_budget_warning()
```

---

## UI/UX Design

### Gradio Interface Additions

#### 1. Image Generation Toggle
**Location**: New section in Gradio app
**Default**: OFF (disabled)
**Design**:
```
┌─────────────────────────────────────────┐
│ 🎨 Visual Slideshow Generation          │
├─────────────────────────────────────────┤
│                                         │
│ [OFF] Enable AI Image Generation        │
│       └─ View Usage & Costs →           │
│                                         │
│ Generation Method:                      │
│ ○ Local (Free, requires GPU)           │
│ ● Cloud API ($0.02/image)              │
│                                         │
│ Remaining Budget: $7.50 / $10.00       │
│ Images Generated: 125 / 500            │
│                                         │
│ [Generate Visual Slideshow] (disabled) │
└─────────────────────────────────────────┘
```

#### 2. Token Usage & Cost Monitoring Page
**Location**: New Gradio tab "💰 Usage"
**Features**:

```
┌─────────────────────────────────────────┐
│ 💰 Token Usage & Cost Monitoring        │
├─────────────────────────────────────────┤
│                                         │
│ Current Period: Nov 2025                │
│                                         │
│ Budget Status:                          │
│ ╔════════════════════════════════════╗  │
│ ║ ████████████░░░░░░░░░░ 75% used    ║  │
│ ╚════════════════════════════════════╝  │
│ $7.50 used of $10.00 budget            │
│                                         │
│ Usage Breakdown:                        │
│ ┌─────────────────────────────────────┐ │
│ │ Image Generation  │ 125 imgs │ $6.25││
│ │ Prompt Generation │ 125 reqs │ $1.25││
│ │ Total             │          │ $7.50││
│ └─────────────────────────────────────┘ │
│                                         │
│ Recent Activity:                        │
│ • 2025-10-30 14:32 - Generated 5 images│
│   Cost: $0.25                           │
│ • 2025-10-30 13:15 - Generated 3 images│
│   Cost: $0.15                           │
│                                         │
│ Cost Per Image: $0.05 avg              │
│ Images Remaining: 50 (est.)            │
│                                         │
│ [Reset Monthly Budget]                  │
│ [Export Usage Report]                   │
└─────────────────────────────────────────┘
```

#### 3. Pre-Generation Cost Preview
**When**: Before generating images
**Design**:
```
┌─────────────────────────────────────────┐
│ ⚠️ Cost Estimate                        │
├─────────────────────────────────────────┤
│                                         │
│ You are about to generate:              │
│ • 5 sentences = 5 images                │
│                                         │
│ Estimated Cost: $0.25                   │
│ Remaining Budget: $7.50 → $7.25        │
│                                         │
│ [Cancel] [Generate ($0.25)]            │
└─────────────────────────────────────────┘
```

---

## Cost Management System

### Budget Tracking Database
**Storage**: SQLite (local, simple)

**Schema**:
```sql
CREATE TABLE usage_log (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    service TEXT,  -- 'local' or 'api_name'
    operation TEXT,  -- 'image_gen' or 'prompt_gen'
    cost REAL,  -- 0 for local, actual cost for API
    details JSON  -- {prompt, model, image_size, etc}
);

CREATE TABLE budget (
    month TEXT PRIMARY KEY,  -- '2025-11'
    limit REAL,  -- 10.00
    spent REAL,  -- 7.50
    updated DATETIME
);
```

### Budget Enforcement
```python
def check_budget(operation_cost: float) -> bool:
    """Check if operation would exceed budget."""
    current_month = get_current_month()
    budget = get_monthly_budget(current_month)

    if budget['spent'] + operation_cost > budget['limit']:
        return False  # Would exceed budget
    return True

def track_usage(service: str, operation: str, cost: float, details: dict):
    """Log usage and update budget."""
    db.execute("""
        INSERT INTO usage_log (timestamp, service, operation, cost, details)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.now(), service, operation, cost, json.dumps(details)))

    update_budget_spent(get_current_month(), cost)

def get_remaining_budget() -> float:
    """Get remaining budget for current month."""
    budget = get_monthly_budget(get_current_month())
    return budget['limit'] - budget['spent']
```

### Rate Limiting
```python
# Prevent abuse even with local generation
MAX_GENERATIONS_PER_HOUR = 100  # Prevent DoS on local GPU
MAX_GENERATIONS_PER_DAY = 500

def check_rate_limit() -> bool:
    """Check if user has exceeded rate limits."""
    hour_count = get_generation_count(hours=1)
    day_count = get_generation_count(hours=24)

    if hour_count >= MAX_GENERATIONS_PER_HOUR:
        return False
    if day_count >= MAX_GENERATIONS_PER_DAY:
        return False
    return True
```

---

## Image Generation Pipeline

### Step 1: Semantic Analysis (FREE with Claude)
**Input**: Semantic Bit JSON
**Output**: Image prompts

```python
def generate_image_prompts(sb_json: dict) -> list[str]:
    """Generate image prompts from semantic triples.

    Uses template-based approach (NO API calls needed).
    """
    prompts = []

    for sentence in sb_json['sentences']:
        if sentence['type'] == 'triple':
            # Point-Line-Point: "The cat sits on the mat"
            prompt = f"{sentence['point1']} {sentence['line1']} {sentence['point2']}, digital art style, high quality"
        elif sentence['type'] == 'point':
            # Just a concept
            prompt = f"{sentence['content']}, digital art illustration, detailed"
        # ... other pattern types

        prompts.append(prompt)

    return prompts
```

**Cost**: $0 (template-based, no AI needed)

**Alternative** (if needed): Use Claude to enhance prompts
- Cost: ~$0.001 per prompt (very cheap)
- Example: "Enhance this for image generation: [semantic text]"
- Total for 10 sentences: ~$0.01

### Step 2: Image Generation
**Input**: Image prompts
**Output**: Generated images

#### Option A: Local Generation (FREE)
```python
from diffusers import StableDiffusionPipeline
import torch

class LocalImageGenerator:
    def __init__(self):
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            safety_checker=None  # Optional, for speed
        )
        if torch.cuda.is_available():
            self.pipe = self.pipe.to("cuda")

    def generate(self, prompt: str) -> Image:
        """Generate image from prompt (FREE)."""
        image = self.pipe(
            prompt,
            num_inference_steps=50,  # Balance quality/speed
            guidance_scale=7.5
        ).images[0]
        return image
```

**Performance**:
- RTX 3060: ~7 seconds per image
- CPU: ~3 minutes per image
- Quality: Excellent

#### Option B: API Generation (PAID)
```python
import together

class APIImageGenerator:
    def __init__(self, api_key: str):
        self.client = together.Together(api_key=api_key)
        self.cost_per_image = 0.005  # $0.005/image on Together.ai

    def generate(self, prompt: str) -> Image:
        """Generate image from prompt (PAID)."""
        # Check budget first
        if not check_budget(self.cost_per_image):
            raise BudgetExceededError()

        response = self.client.images.generate(
            prompt=prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            steps=50
        )

        # Track cost
        track_usage('together_ai', 'image_gen', self.cost_per_image, {
            'prompt': prompt,
            'model': 'sdxl-base-1.0'
        })

        return response.data[0]
```

**Cost**: $0.005 per image = 2000 images for $10

### Step 3: Slideshow Composition
**Input**: Generated images
**Output**: Animated slideshow (HTML or video)

```python
def create_visual_slideshow(images: list[Image], timing_ms: int = 3000) -> str:
    """Create HTML slideshow with generated images."""
    html = "<html><body><style>..."

    for idx, image in enumerate(images):
        # Embed image as base64
        img_data = image_to_base64(image)
        delay = idx * timing_ms

        html += f"""
        <div class="slide" style="animation-delay: {delay}ms">
            <img src="data:image/png;base64,{img_data}" />
        </div>
        """

    html += "</body></html>"
    return html
```

---

## Implementation Phases

### Phase 0: Planning (Current) ✅
- [x] Define budget constraints
- [x] Research local vs API options
- [x] Design UI/UX mockups
- [x] Cost analysis

### Phase 1: Cost Tracking Infrastructure (1-2 days)
**Goal**: Build budget monitoring before any generation

**Tasks**:
- [ ] Create SQLite database schema
- [ ] Implement budget tracking functions
- [ ] Build usage logging system
- [ ] Create cost calculation utilities
- [ ] Add rate limiting

**Deliverable**: Working cost tracking (no generation yet)

### Phase 2: Local Generation (3-5 days)
**Goal**: Free image generation for GPU users

**Tasks**:
- [ ] Install and test Stable Diffusion locally
- [ ] Create Python wrapper for generation
- [ ] GPU detection and fallback logic
- [ ] Optimize generation speed
- [ ] Cache generated images (avoid regeneration)

**Deliverable**: Local image generation working

### Phase 3: Gradio Integration (2-3 days)
**Goal**: Add UI controls to Gradio app

**Tasks**:
- [ ] Add toggle button (OFF by default)
- [ ] Create "Usage & Costs" monitoring tab
- [ ] Add cost preview before generation
- [ ] Wire up generation to Gradio
- [ ] Test with sample inputs

**Deliverable**: Full UI integration

### Phase 4: API Fallback (2-3 days)
**Goal**: Paid option for users without GPU

**Tasks**:
- [ ] Integrate Together.ai API
- [ ] Implement budget checks before API calls
- [ ] Add API key configuration
- [ ] Test cost tracking with real API
- [ ] Document API setup

**Deliverable**: API generation with cost controls

### Phase 5: Slideshow Composition (1-2 days)
**Goal**: Combine images into animated slideshow

**Tasks**:
- [ ] HTML slideshow template
- [ ] Image embedding (base64)
- [ ] Timing synchronization
- [ ] Download functionality
- [ ] Test with various inputs

**Deliverable**: Complete visual slideshows

**Total Estimated Time**: 9-15 days

---

## Cost Projections

### $10/month Budget Scenarios

#### Scenario A: 100% Local (FREE)
- **Cost**: $0/month
- **Capacity**: Unlimited
- **Requirements**: GPU with 4GB+ VRAM
- **Users**: Those with gaming PCs, dev machines

#### Scenario B: 100% API (Together.ai)
- **Cost per image**: $0.005
- **Budget**: $10/month
- **Capacity**: 2000 images/month
- **Daily limit**: ~66 images/day
- **Per session**: ~10 stories (10 sentences each)

#### Scenario C: Mixed Usage (Realistic)
- **80% local** (users with GPU): $0
- **20% API** (users without GPU): $10
- **Effective capacity**: 400 API images + unlimited local
- **Sufficient for**: ~40 API users + unlimited local users

### Budget Expansion Scenarios

| Budget | Together.ai | DALL-E 3 | Stability AI |
|--------|-------------|----------|--------------|
| $10    | 2000 imgs   | 250 imgs | 500 imgs     |
| $50    | 10,000 imgs | 1250 imgs| 2500 imgs    |
| $100   | 20,000 imgs | 2500 imgs| 5000 imgs    |

**Recommendation**: Start with Together.ai ($10 = 2000 images), expand if needed

---

## Risk Mitigation

### Risk 1: Budget Overrun
**Mitigation**:
- Hard budget cap (stops at $10)
- Cost preview before generation
- Monthly reset with user notification
- Rate limiting (prevent accidental spam)

### Risk 2: Poor Image Quality
**Mitigation**:
- Use proven models (Stable Diffusion 1.5/XL)
- Optimize prompts with templates
- Allow user to regenerate if unsatisfied
- Quality settings (fast/balanced/quality)

### Risk 3: Slow Generation
**Mitigation**:
- GPU acceleration when available
- Async generation (show progress)
- Batch processing for multiple images
- Cache results to avoid regeneration

### Risk 4: Setup Complexity (Local)
**Mitigation**:
- Detailed installation guide
- Auto-detection of GPU
- Fallback to API if setup fails
- Docker container option (pre-configured)

---

## Technical Requirements

### For Local Generation
**Minimum**:
- Python 3.9+
- 10GB free disk space
- 8GB RAM
- GPU: 4GB VRAM (optional but recommended)

**Recommended**:
- Python 3.10+
- 20GB free disk space
- 16GB RAM
- GPU: 8GB+ VRAM (RTX 3060 or better)

**Packages**:
```bash
pip install diffusers transformers torch torchvision
pip install accelerate safetensors
```

### For API Generation
**Requirements**:
- API key (Together.ai account)
- Internet connection
- Minimal local resources

---

## Next Steps

### Immediate (This Week)
1. **Review this plan** - Approve architecture and budget strategy
2. **Choose priority** - When to start (after Phase 4? Sooner?)
3. **Test local setup** - Install Stable Diffusion and test on your machine

### Before Starting Implementation
1. **Verify GPU** - Check if you have NVIDIA GPU with 4GB+ VRAM
2. **Get API key** - Sign up for Together.ai (if needed as fallback)
3. **Disk space** - Ensure 10-20GB free for models
4. **Budget approval** - Confirm $10/month budget

### Phase 1 Kickoff
1. Set up cost tracking database
2. Create monitoring dashboard
3. Test budget enforcement
4. Prepare for local generation

---

## Questions to Answer

1. **GPU Availability**: Do you have an NVIDIA GPU? What model?
2. **Primary Method**: Local (free) or API (paid) as default?
3. **Image Quality**: Prefer speed or quality?
4. **Storage**: OK with 10-20GB for models?
5. **Timeline**: When to start? (After Phase 4 patterns? Sooner?)

---

**Budget**: $10/month (expandable)
**Strategy**: Local-first (free), API fallback (paid with strict limits)
**Cost Tracking**: Required (dashboard + hard caps)
**Default**: OFF (user must opt-in)
**Status**: Ready to implement when prioritized
