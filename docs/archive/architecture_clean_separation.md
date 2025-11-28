# Clean Architecture - AI Image Generation
**Date**: 2025-10-31
**Status**: Architecture Planning - For Future Implementation
**Purpose**: Separate concerns between pip package, GPU server, and Django application

---

## Overview

This document defines the clean separation of concerns for implementing AI image generation across three distinct components:

1. **semantic_bit_theory** (pip package) - Pure logic library
2. **semantic_bit_gpu_server** (microservice) - Standalone image generation service
3. **newdreamflow** (Django app) - Application orchestration

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│  newdreamflow (Django Application)              │
│                                                  │
│  Uses:                                           │
│    1. pip install semantic_bit (library)         │
│    2. HTTP calls to GPU server (service)         │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
┌──────────────────┐  ┌─────────────────────┐
│  semantic_bit    │  │  GPU Server         │
│  (pip package)   │  │  (microservice)     │
│                  │  │                     │
│  Pure logic:     │  │  Infrastructure:    │
│  - Encode        │  │  - FastAPI          │
│  - Decode        │  │  - Stable Diffusion │
│  - SVG gen       │  │  - GPU inference    │
│  - Prompt gen    │  │  - Auth/limits      │
│                  │  │                     │
│  NO server code  │  │  NO semantic logic  │
│  NO GPU code     │  │  GENERIC service    │
└──────────────────┘  └─────────────────────┘
```

---

## Component 1: semantic_bit_theory (pip package)

### Role
Pure Python library for semantic encoding/decoding with no infrastructure dependencies.

### Proposed Structure
```
semantic_bit_theory/
├── semantic_bit/           # The pip package
│   ├── src/semantic_bit/
│   │   ├── encoder.py              # Text → Semantic Bit JSON
│   │   ├── decoder.py              # Semantic Bit JSON → formats
│   │   ├── svg_animation.py        # Generate SVG animations
│   │   ├── pattern_detector.py     # Pattern analysis
│   │   └── ai/
│   │       └── prompt_generator.py # Semantic Bit → AI prompts (pure logic)
│   └── tests/
├── gradio_app/             # Testing tool (not published to pip)
│   └── app.py              # For visualizing encoding/decoding/SVG
├── docs/                   # Core library docs
└── setup.py                # Publishes semantic_bit package
```

### What It SHOULD Include
- ✅ Text encoding/decoding
- ✅ SVG animation generation
- ✅ Pattern detection
- ✅ AI prompt generation (pure logic, no API calls)
- ✅ Gradio testing UI (for development, not in pip)

### What It Should NOT Include
- ❌ GPU/CUDA code
- ❌ Stable Diffusion models
- ❌ FastAPI servers
- ❌ Heavy dependencies (torch, diffusers)
- ❌ HTTP servers or API clients
- ❌ Image generation implementation

### Dependencies
**Minimal only:**
- Standard library
- Lightweight parsing libraries
- NO torch, NO diffusers, NO API clients

### Example Usage
```python
# Pure logic - converts semantic meaning to optimized prompt
from semantic_bit import encode_text_to_sb
from semantic_bit.ai import generate_image_prompt

sb = encode_text_to_sb("The cat sits on the mat")
prompt = generate_image_prompt(sb)
# Returns: "a cat sitting on a mat, digital art style"
```

### Key Decision: Prompt Generation Logic
**Add to pip package**: `semantic_bit.ai.prompt_generator`

**Why:**
- Pure Python logic (no GPU needed)
- Reusable by any application
- Testable without infrastructure
- Part of semantic bit "knowledge"

**Function signature:**
```python
def generate_image_prompt(sb_dict: dict, style: str = "digital art") -> str:
    """
    Convert semantic bit structure to optimized image generation prompt.

    Args:
        sb_dict: Semantic bit JSON structure
        style: Art style preference

    Returns:
        Optimized prompt string
    """
    # Analyzes semantic structure
    # Extracts key elements (subject, action, object)
    # Constructs optimized prompt
    # NO API calls, NO GPU, pure logic
    pass
```

---

## Component 2: semantic_bit_gpu_server (separate repo)

### Role
Standalone microservice for AI image generation. Generic service - doesn't know about semantic bits.

### Repository
**Separate GitHub repo**: `semantic_bit_gpu_server` (or similar name)

**Why separate:**
1. Could serve multiple projects (not just semantic bit)
2. Different deployment lifecycle (infrastructure vs. application)
3. Different tech stack (FastAPI vs. Django)
4. Can be developed/tested independently
5. Dan or others could run their own instance
6. Heavy dependencies isolated from pip package

### Proposed Structure
```
semantic_bit_gpu_server/
├── server/
│   ├── main.py              # FastAPI server
│   ├── stable_diffusion.py  # GPU inference
│   ├── auth.py              # API key management
│   ├── rate_limiter.py      # Budget controls
│   └── usage_tracker.py     # Cost tracking
├── docs/
│   ├── windows_setup.md     # Your Windows PC setup
│   ├── tailscale_setup.md   # Remote access setup
│   └── security.md          # Security best practices
├── scripts/
│   └── setup_windows.sh     # Automated setup
├── requirements.txt         # torch, diffusers, fastapi, etc.
└── README.md
```

### API Contract
**Generic image generation API:**

```python
POST /generate
{
    "prompt": "a cat sitting on a mat, digital art",
    "api_key": "secret",
    "width": 512,
    "height": 512,
    "steps": 50
}

Response:
{
    "image": "base64...",
    "cost": 0.0,              # Free for local GPU
    "generation_time": 4.2,
    "model": "stable-diffusion-v1-5"
}

GET /usage
{
    "api_key": "secret",
    "month": "2025-10"
}

Response:
{
    "month": "2025-10",
    "images_generated": 150,
    "total_cost": 0.0,
    "gpu_hours": 0.125
}

GET /health
Response:
{
    "status": "ok",
    "gpu_available": true,
    "model_loaded": true
}
```

### Key Features
- FastAPI server
- Stable Diffusion on CUDA
- API key authentication
- Rate limiting
- Usage tracking
- Budget enforcement
- Health checks

### What It Should NOT Include
- ❌ Semantic bit logic
- ❌ Application-specific business rules
- ❌ Django integration
- ❌ UI components

**Keep it generic** - any application can use it.

---

## Component 3: newdreamflow (Django application)

### Role
Application orchestration - combines semantic_bit + GPU server to deliver features.

### How It Uses Other Components

```python
# In Django view/service
from semantic_bit import encode_text_to_sb
from semantic_bit.ai import generate_image_prompt
import requests
from django.conf import settings

def generate_semantic_image(user_text: str):
    # 1. Encode text (using pip library)
    sb = encode_text_to_sb(user_text)

    # 2. Generate optimized prompt (using pip library)
    prompt = generate_image_prompt(sb, style="digital art")

    # 3. Call GPU server (separate service)
    response = requests.post(
        settings.GPU_SERVER_URL + "/generate",
        json={
            "prompt": prompt,
            "api_key": settings.GPU_API_KEY,
            "width": 512,
            "height": 512
        }
    )

    # 4. Return to user
    return {
        "image": response.json()["image"],
        "semantic_structure": sb,
        "prompt_used": prompt
    }
```

### Dependencies
- `pip install semantic_bit` (the pip package)
- GPU server URL in Django settings
- Standard Django dependencies

### Configuration
```python
# settings.py
GPU_SERVER_URL = "http://192.168.1.100:8000"  # Your Windows PC (local)
# Or: GPU_SERVER_URL = "http://100.x.x.x:8000"  # Via Tailscale (remote)
GPU_API_KEY = env("GPU_API_KEY")
```

---

## What Goes Where - Decision Matrix

| Feature | semantic_bit (pip) | GPU Server | newdreamflow |
|---------|-------------------|------------|--------------|
| **Core Logic** |
| Encoding/decoding | ✅ YES | ❌ No | ❌ No (uses pip) |
| SVG generation | ✅ YES | ❌ No | ❌ No (uses pip) |
| Pattern detection | ✅ YES | ❌ No | ❌ No (uses pip) |
| Prompt generation | ✅ YES (logic only) | ❌ No | ❌ No (uses pip) |
| **Infrastructure** |
| Image generation | ❌ No | ✅ YES | ❌ No (calls server) |
| GPU/CUDA | ❌ No | ✅ YES | ❌ No |
| FastAPI server | ❌ No | ✅ YES | ❌ No |
| Stable Diffusion | ❌ No | ✅ YES | ❌ No |
| **Application** |
| Django web UI | ❌ No | ❌ No | ✅ YES |
| User management | ❌ No | ❌ No | ✅ YES |
| Business logic | ❌ No | ❌ No | ✅ YES |
| **Cross-cutting** |
| Cost tracking | ❌ No | ✅ YES (tracks) | ✅ YES (displays) |
| API authentication | ❌ No | ✅ YES (validates) | ✅ YES (stores key) |
| Gradio testing | ✅ YES (basic) | ❌ No | Could add |

---

## Development Workflow

### Phase 1: Jack's Windows GPU Setup
**Location**: Your home Windows PC
**Who**: You (Dan can watch via screen share)

**Tasks**:
- [ ] Install Python 3.10/3.11
- [ ] Install CUDA 11.8 or 12.1
- [ ] Install PyTorch with GPU support
- [ ] Download Stable Diffusion model
- [ ] Test local generation
- [ ] Benchmark RTX 4070 Super

### Phase 2: GPU Server Development
**Location**: New repo (`semantic_bit_gpu_server`)
**Deployment**: Your Windows PC

**Tasks**:
- [ ] Create FastAPI server
- [ ] Integrate Stable Diffusion
- [ ] Add authentication
- [ ] Add rate limiting
- [ ] Add usage tracking
- [ ] Test from your Mac

### Phase 3: Pip Package Extension
**Location**: `semantic_bit_theory` repo
**What**: Add `semantic_bit.ai.prompt_generator`

**Tasks**:
- [ ] Create `semantic_bit/src/semantic_bit/ai/` module
- [ ] Implement `generate_image_prompt()` function
- [ ] Add tests (no GPU needed - pure logic)
- [ ] Update pip package version
- [ ] Publish to PyPI

### Phase 4: newdreamflow Integration
**Location**: `newdreamflow` Django repo
**What**: Wire everything together

**Tasks**:
- [ ] `pip install semantic_bit` (updated version)
- [ ] Add GPU_SERVER_URL to settings
- [ ] Create Django service layer
- [ ] Build UI for image generation
- [ ] Add cost monitoring dashboard
- [ ] Test complete workflow

### Phase 5: Remote Access (Optional)
**When**: After local setup proven secure
**How**: Tailscale VPN mesh

**Tasks**:
- [ ] Install Tailscale on Windows PC
- [ ] Dan installs Tailscale
- [ ] Approve Dan's device
- [ ] Test remote access

---

## Network & Security

### Local Development (Phase 1-4)
```
Your Mac → Your Windows PC (same LAN)
192.168.x.x:8000

Security:
- API key authentication
- Windows firewall (allow your Mac IP only)
- NOT exposed to internet
```

### Remote Access (Phase 5)
```
Dan's PC → Tailscale VPN → Your Windows PC
100.x.x.x:8000

Security:
- Tailscale encrypted tunnel
- API key still required
- You control device approval
- No port forwarding needed
```

### Future Public Hosting
**NOT recommended for home network**

**Options:**
1. **Keep private** - Tailscale only (safest)
2. **Deploy to cloud** - Run GPU server on AWS/GCP (if budget allows)
3. **Never** - Direct port forwarding (too risky)

---

## Key Decisions to Finalize

### Decision 1: Prompt Generation Logic
**Question**: Add `semantic_bit.ai.prompt_generator` to pip package?

**Recommendation**: YES
- Pure Python logic (no GPU needed)
- Reusable by any application
- Testable independently
- Part of semantic bit knowledge domain

**Status**: 🟡 To be decided

---

### Decision 2: GPU Server Repo
**Question**: Create separate `semantic_bit_gpu_server` repo?

**Recommendation**: YES - Separate repo
- Different lifecycle (infrastructure vs. library)
- Could serve other projects
- Can be open-sourced independently
- Isolates heavy dependencies

**Repo name options:**
- `semantic_bit_gpu_server`
- `stable-diffusion-api-server`
- `gpu-image-service`

**Status**: 🟡 To be decided

---

### Decision 3: Cost Tracking
**Question**: Where should cost tracking live?

**Recommendation**: Both
- **GPU server**: Tracks actual usage (source of truth)
- **newdreamflow**: Queries and displays to users

**Status**: 🟡 To be decided

---

## Benefits of This Architecture

### Separation of Concerns
- ✅ Pip package stays lightweight and reusable
- ✅ GPU server is generic infrastructure
- ✅ Django app orchestrates without bloat

### Reusability
- ✅ Semantic bit library can be used by any Python project
- ✅ GPU server can serve multiple applications
- ✅ Each component can evolve independently

### Testability
- ✅ Pip package tested without GPU
- ✅ GPU server tested independently
- ✅ Django app tested with mocked GPU calls

### Deployment Flexibility
- ✅ Pip package deployed via PyPI
- ✅ GPU server runs on your Windows PC (or cloud later)
- ✅ Django app deployed separately (cloud, local, etc.)

### Maintainability
- ✅ Clear boundaries
- ✅ Single responsibility per component
- ✅ Easy to reason about each piece

---

## Timeline Estimate

### Phase 1: Windows GPU Setup
**Duration**: 1 week
**Effort**: You, with Dan watching

### Phase 2: GPU Server Development
**Duration**: 1-2 weeks
**Effort**: New repo, FastAPI implementation

### Phase 3: Pip Package Extension
**Duration**: 3-5 days
**Effort**: Add prompt generation module

### Phase 4: newdreamflow Integration
**Duration**: 1-2 weeks
**Effort**: Django service layer + UI

### Phase 5: Remote Access
**Duration**: 1-2 days
**Effort**: Tailscale setup

**Total**: 4-6 weeks

---

## Next Steps (When Ready)

1. **Finalize decisions** - Confirm architecture choices
2. **Create GPU server repo** - If separate repo chosen
3. **Start Phase 1** - Windows GPU setup
4. **Extend pip package** - Add prompt generation module
5. **Integrate into newdreamflow** - Complete the loop

---

## References

- [AI Image Generation Plan](ai_image_generation_plan.md) - Budget and cost strategy
- [GPU Setup Options](gpu_setup_options.md) - Hardware and networking
- [Project Roadmap](project_roadmap.md) - Overall project direction

---

**Status**: Architecture Planning Complete
**Next**: Finalize decisions when ready to implement
**Created**: 2025-10-31
**Last Updated**: 2025-10-31
