# GPU Utilization Strategy - RTX 4070 Super
**Date**: 2025-10-30
**Status**: Planning Phase - Architecture Design
**GPU**: NVIDIA RTX 4070 Super (12GB VRAM)
**Primary Dev**: macOS → Remote GPU on Windows

---

## Hardware Specification

### RTX 4070 Super Capabilities
**Your GPU**: NVIDIA RTX 4070 Super
- **VRAM**: 12GB GDDR6X
- **CUDA Cores**: 7168
- **Performance**: Excellent for Stable Diffusion
- **Generation Speed**: ~3-5 seconds per image (512x512), ~5-8 seconds (1024x1024)
- **Quality**: Professional-grade

### Comparison to Requirements
| Requirement | RTX 4070 Super | Status |
|------------|----------------|--------|
| Minimum VRAM | 4GB | ✅ 12GB (3x over) |
| Recommended VRAM | 8GB | ✅ 12GB (1.5x over) |
| CUDA Support | Required | ✅ 7168 cores |
| Generation Speed | < 30s | ✅ ~5s (6x faster) |

**Verdict**: Ideal GPU for this project. Can run largest models with room to spare.

---

## Architecture Options

### Option 1: Direct Windows Development (Simplest)
**What**: Develop on Windows machine with GPU

**Pros**:
- ✅ Direct GPU access (fastest)
- ✅ No network latency
- ✅ Simplest setup
- ✅ Best performance

**Cons**:
- ⚠️ Different dev environment (Windows vs macOS)
- ⚠️ May need to sync code between machines
- ⚠️ Windows-specific quirks

**Setup**:
```bash
# On Windows machine
git clone https://github.com/your-repo/semantic_bit_theory.git
cd semantic_bit_theory
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install diffusers transformers torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Recommended For**: When actively developing image generation features

---

### Option 2: Remote GPU Server (Recommended)
**What**: Run GPU as a service, access from Mac

**Architecture**:
```
┌─────────────┐         HTTP/gRPC        ┌──────────────┐
│  Mac        │ ───────────────────────> │  Windows PC  │
│  (Dev)      │  Send prompts            │  (GPU Server)│
│             │ <─────────────────────── │              │
│  Gradio App │  Receive images          │  Stable Diff │
└─────────────┘                          └──────────────┘
```

**Pros**:
- ✅ Develop on Mac (preferred environment)
- ✅ GPU available when needed
- ✅ Can use from any machine on network
- ✅ Windows machine can do other tasks
- ✅ No code duplication

**Cons**:
- ⚠️ Network latency (~100-500ms)
- ⚠️ Requires Windows PC to be running
- ⚠️ Initial setup complexity

**Implementation Approaches**:

#### 2A: REST API Server (Simple)
**What**: Flask/FastAPI server on Windows serving image generation

**Windows Server Code**:
```python
from fastapi import FastAPI
from diffusers import StableDiffusionPipeline
import torch
import base64
from io import BytesIO

app = FastAPI()

# Load model once on startup
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

@app.post("/generate")
def generate_image(prompt: str):
    """Generate image from prompt."""
    image = pipe(prompt, num_inference_steps=50).images[0]

    # Convert to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return {"image": img_str}

# Run: uvicorn server:app --host 0.0.0.0 --port 8000
```

**Mac Client Code**:
```python
import requests

def generate_image_remote(prompt: str):
    """Call Windows GPU server from Mac."""
    response = requests.post(
        "http://windows-pc-ip:8000/generate",
        json={"prompt": prompt}
    )
    return response.json()["image"]
```

**Setup Time**: ~1 hour
**Complexity**: Low

#### 2B: gRPC Server (Production-Grade)
**What**: High-performance RPC for faster communication

**Pros over REST**:
- ✅ Lower latency
- ✅ Streaming support
- ✅ Binary protocol (faster)
- ✅ Type safety

**Setup Time**: ~2-3 hours
**Complexity**: Medium

#### 2C: ComfyUI API (Advanced)
**What**: Use ComfyUI's web interface as image generation server

**Pros**:
- ✅ Visual workflow editor
- ✅ Advanced features (upscaling, inpainting, etc.)
- ✅ Web UI for testing
- ✅ REST API built-in

**Cons**:
- ⚠️ More complex setup
- ⚠️ Heavier resource usage

**Setup Time**: ~2-4 hours
**Complexity**: Medium-High

---

### Option 3: Cloud GPU Service (Backup)
**What**: Rent GPU in cloud when Windows PC unavailable

**Services**:
- RunPod: $0.20-0.40/hour (RTX 3090/4090)
- Vast.ai: $0.15-0.30/hour (various GPUs)
- Lambda Labs: $0.50-1.00/hour (guaranteed availability)

**Use Case**: When Windows PC is off or unavailable

**Cost Analysis** (assuming 2 hours/week):
- Weekly: ~$1.60 (RunPod)
- Monthly: ~$6.40
- **Still under $10 budget**

**Recommended**: Keep as backup option

---

### Option 4: Hybrid Approach (Best of All Worlds)
**What**: Auto-detect and use best available option

**Priority Order**:
1. **Local GPU** (Windows PC on network) - FREE, fast
2. **Cloud GPU** (if Windows PC off) - Cheap, reliable
3. **API fallback** (Together.ai) - Cheapest API, budget-limited

**Implementation**:
```python
def generate_image(prompt: str) -> Image:
    """Smart image generation with fallback."""

    # Try local GPU first (FREE)
    if check_windows_server_available():
        try:
            return generate_remote_gpu(prompt)
        except Exception as e:
            log_error(f"Local GPU failed: {e}")

    # Fallback to cloud GPU (CHEAP)
    if cloud_gpu_available():
        try:
            return generate_cloud_gpu(prompt)
        except Exception as e:
            log_error(f"Cloud GPU failed: {e}")

    # Last resort: API (BUDGET-LIMITED)
    if check_budget_available():
        return generate_api(prompt)
    else:
        raise BudgetExceededError()
```

**Pros**:
- ✅ Always available (3 fallback layers)
- ✅ Cost-optimized (uses free when possible)
- ✅ Reliable (multiple failure recovery)

**Cons**:
- ⚠️ More complex to implement
- ⚠️ More things that can go wrong

---

## Recommended Architecture

### Phase 1: Simple Remote Server (Start Here)
**Timeline**: Implement first
**Approach**: Option 2A (REST API)
**Cost**: $0 (use your RTX 4070 Super)

**Setup**:
1. Install Python + dependencies on Windows
2. Download Stable Diffusion model (~4GB)
3. Run FastAPI server
4. Connect from Mac Gradio app
5. Test generation

**Benefits**:
- Simple to implement
- No cost
- Good performance
- Easy to debug

### Phase 2: Add Cloud Fallback (Later)
**Timeline**: Add when needed
**Approach**: RunPod integration
**Cost**: ~$6/month (only when Windows PC unavailable)

**Use Case**: Development while traveling, Windows PC maintenance, etc.

### Phase 3: Full Hybrid (Production)
**Timeline**: Polish phase
**Approach**: Option 4 (Auto-fallback)
**Cost**: Minimal (mostly free local)

---

## Network Setup

### Local Network (Mac ↔ Windows)
**Requirements**:
- Both machines on same network (WiFi/Ethernet)
- Windows firewall allows port 8000
- Know Windows PC's IP address

**Find Windows IP**:
```cmd
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

**Test Connection from Mac**:
```bash
curl http://192.168.1.100:8000/health
# Should return {"status": "ok"}
```

### Port Forwarding (Remote Access)
**If you want to access from outside home network**:

**Option A**: Tailscale (Recommended)
- Free VPN mesh network
- Secure, encrypted
- Works anywhere
- No port forwarding needed

**Option B**: ngrok (Quick Testing)
- Tunnel to public URL
- Free tier available
- Good for demos

**Option C**: Manual Port Forwarding
- Configure router
- Security risk (need auth)
- More complex

**Recommendation**: Start with local network, add Tailscale if needed later

---

## Performance Projections

### RTX 4070 Super Generation Speeds

| Resolution | Steps | Time (est.) | Quality |
|-----------|-------|-------------|---------|
| 512x512   | 20    | ~2s         | Good    |
| 512x512   | 50    | ~4s         | Better  |
| 768x768   | 50    | ~6s         | Better+ |
| 1024x1024 | 50    | ~8s         | Best    |

**For semantic bit slideshows**:
- 5 sentences = 5 images
- 512x512, 50 steps each
- Total time: ~20 seconds
- Quality: Excellent for web display

**Network Overhead**:
- Local network: +200-500ms per image
- Image transfer (base64): +100-300ms
- Total: ~25-30 seconds for 5 images

**Still very fast!**

---

## Storage Requirements

### Model Storage (Windows PC)
**Stable Diffusion v1.5**: ~4GB
**Stable Diffusion XL**: ~7GB
**VAE (optional)**: ~330MB
**Total (recommended)**: ~10-15GB

**Your 12GB VRAM can run**:
- ✅ SD 1.5 (4GB model, fits easily)
- ✅ SD XL (7GB model, fits comfortably)
- ✅ Multiple models simultaneously

### Generated Image Cache
**Per image**: ~500KB (512x512 PNG)
**100 images**: ~50MB
**1000 images**: ~500MB

**Recommendation**: Cache on Windows PC, transfer to Mac as needed

---

## Security Considerations

### Local Network Server
**Risks**:
- Anyone on network can access GPU
- Potential DoS (spam requests)
- No authentication by default

**Mitigations**:
1. **API Key Authentication**:
```python
@app.post("/generate")
def generate_image(prompt: str, api_key: str):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(401, "Invalid API key")
    # ... generate image
```

2. **Rate Limiting**:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/generate")
@limiter.limit("10/minute")  # Max 10 requests per minute
def generate_image(prompt: str):
    # ... generate image
```

3. **HTTPS (if external access)**:
```bash
# Use Let's Encrypt or self-signed cert
uvicorn server:app --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### External Access
**Recommendations**:
- ✅ Use Tailscale (encrypted VPN)
- ✅ API key authentication
- ✅ Rate limiting
- ❌ Avoid direct port forwarding (security risk)

---

## Development Workflow

### Typical Day (Mac Development)
1. **Morning**: Start Windows PC, launch GPU server
2. **Development**: Code on Mac, test with remote GPU
3. **Testing**: Generate images via network
4. **Evening**: Stop GPU server, shut down Windows PC

### Alternative: Always-On Server
- Keep Windows PC running 24/7
- Access GPU anytime
- **Cost**: ~$10-20/month electricity (RTX 4070 Super idle)
- **Benefit**: Always available

### Hybrid Workflow
- **Active dev**: Use Windows PC directly
- **Mac dev**: Remote GPU server
- **Travel/backup**: Cloud GPU (RunPod)

---

## Cost Comparison

### Setup Costs
| Option | Initial | Monthly | Notes |
|--------|---------|---------|-------|
| Local GPU (yours) | $0 | $0 | Free unlimited! |
| Cloud GPU (RunPod) | $0 | ~$6 | Only when needed |
| API (Together.ai) | $0 | ~$10 | Budget-limited |
| DALL-E 3 | $0 | ~$250 | Would exceed budget |

**Your Advantage**: RTX 4070 Super saves ~$250/month vs DALL-E!

### Operational Costs
**Local GPU**:
- Electricity: ~$5-10/month (if always on)
- Maintenance: $0
- **Total**: ~$10/month maximum

**Cloud GPU**:
- RunPod: $0.30/hour × 20 hours = $6/month
- Vast.ai: $0.20/hour × 20 hours = $4/month
- **Total**: ~$6/month (backup only)

**Combined Strategy**:
- Primary: Local GPU ($0 generation + ~$5 electricity)
- Backup: Cloud GPU (~$6/month when needed)
- **Total**: ~$11/month worst case (still under budget!)

---

## Implementation Priorities

### Phase 1: Windows Direct Development (Week 1)
**Goal**: Get local generation working
**Tasks**:
1. Install Python on Windows
2. Install PyTorch + CUDA
3. Install Stable Diffusion
4. Test generation locally
5. Optimize settings

**Deliverable**: Working image generation on Windows

### Phase 2: Remote Server Setup (Week 2)
**Goal**: Access from Mac
**Tasks**:
1. Create FastAPI server on Windows
2. Test API endpoints
3. Connect Gradio on Mac
4. Add authentication
5. Test image generation pipeline

**Deliverable**: Mac → Windows GPU working

### Phase 3: Integration & Polish (Week 3)
**Goal**: Full Gradio integration
**Tasks**:
1. Add toggle button (OFF by default)
2. Create cost monitoring (even though local is free)
3. Add generation preview
4. Cache results
5. Error handling & fallbacks

**Deliverable**: Complete feature in Gradio

### Phase 4: Cloud Backup (Week 4, Optional)
**Goal**: Fallback when Windows off
**Tasks**:
1. Set up RunPod account
2. Integrate cloud API
3. Add auto-detection
4. Test fallback logic

**Deliverable**: Always-available generation

---

## Technical Specifications

### Windows Server Requirements
**OS**: Windows 10/11
**Python**: 3.10 or 3.11 (3.9+ works, 3.14 too new)
**CUDA**: 11.8 or 12.1
**Disk Space**: 20GB free (for models and cache)
**Network**: Stable connection to Mac

### Mac Client Requirements
**Python**: 3.9+ (same as dev environment)
**Network**: Access to Windows PC (local network)
**Gradio**: Already installed
**Additional**: `requests` library (for HTTP calls)

### Network Requirements
**Bandwidth**: ~1-2 Mbps (for image transfer)
**Latency**: < 100ms (local network)
**Reliability**: Stable connection preferred

---

## Next Steps for Codex Review

### Questions for Codex
1. **Architecture**: REST API (simple) vs gRPC (performant)?
2. **Security**: API key auth sufficient or need OAuth?
3. **Caching**: Where to cache? (Windows, Mac, or both)
4. **Error handling**: How graceful should fallbacks be?
5. **Monitoring**: Track generation stats even for free local?

### Questions for Dan (Windows Expert)
1. **Setup**: Can help with Windows Python/CUDA setup?
2. **Networking**: Firewall configuration assistance?
3. **Testing**: Can test Windows server on his machine?
4. **Security**: Any Windows-specific security concerns?

### Questions for User (Jack)
1. **Network**: Is Windows PC on same network as Mac?
2. **Availability**: Will Windows PC be running during dev?
3. **Preference**: Start with Windows-direct or remote server?
4. **Timeline**: When to start implementation? (After patterns or sooner)

---

## Decision Matrix

### Choose Your Path

| Scenario | Recommended Option | Reasoning |
|----------|-------------------|-----------|
| **Windows PC always on** | Option 2A (REST Server) | Free, fast, simple |
| **Windows PC sometimes off** | Option 4 (Hybrid) | Fallbacks ensure availability |
| **Want simplest setup** | Option 1 (Direct Windows) | No network complexity |
| **Want best performance** | Option 2B (gRPC) | Lowest latency |
| **Want flexibility** | Option 4 (Hybrid) | All options available |

### Our Recommendation
**Start**: Option 2A (REST API Server)
- Simple to implement
- Good performance
- Easy to debug
- Can add fallbacks later

**Later**: Add Option 4 (Hybrid) when needed

---

## Success Metrics

### Performance Goals
- [ ] Image generation: < 10 seconds per image
- [ ] End-to-end (5 images): < 1 minute
- [ ] Network latency: < 500ms
- [ ] Server uptime: > 95% during dev hours

### Cost Goals
- [ ] Monthly cost: < $10 (achieved with free local!)
- [ ] Image budget: Unlimited (local)
- [ ] Backup API: < $5/month (cloud GPU)

### Quality Goals
- [ ] Image quality: Comparable to DALL-E
- [ ] Prompt accuracy: > 80% (match semantic intent)
- [ ] User satisfaction: "Good enough" for prototype

---

**Status**: Documented for Codex + Dan review
**Next**: Await feedback, then implement when prioritized
**Hardware**: RTX 4070 Super (12GB) - Excellent choice!
**Strategy**: Local-first (free), cloud backup (cheap), API fallback (budget-limited)
