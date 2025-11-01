# Claude Context - Semantic Bit Theory Project

**Last Updated**: 2025-10-31
**Current Phase**: Phase 1 Complete ✅ → Ready for Phase 2
**Project**: AI Image Generation for Semantic Bit Visualizations

---

## Project Overview

**Semantic Bit Theory**: A novel approach to encoding natural language text into structured semantic representations using Point terms (entities/concepts) and Line terms (relationships/actions).

**Current Goal**: Add AI image generation capability to create visual slideshows from Semantic Bit encoded text.

**Timeline**: 11-12 week implementation (Week 1-2 complete)

---

## Repository Structure

### This Repository (`semantic_bit_theory`)
**Owner**: Dan (antfriend) - https://github.com/antfriend/semantic_bit_theory
**Your Role**: Collaborator
**Purpose**: Project documentation hub, architecture, planning
**Role**: Central reference for all implementation work

### Related Repositories

1. **`semantic_bit`** (Python package)
   - Published on PyPI
   - Core encoding/decoding functionality
   - **Phase 3**: Will add `semantic_bit/ai/prompt_generator.py`

2. **`semantic_bit_gpu_server`** (NEW - To be created)
   - Standalone FastAPI microservice
   - Stable Diffusion image generation
   - **Phase 2**: Primary implementation target
   - **Status**: Not yet created (create after Codex review)

3. **`newdreamflow`** (Gradio app)
   - User interface
   - **Phase 4**: Integration with GPU server

---

## Current Status (2025-10-31)

### ✅ Phase 0: Planning & Architecture (COMPLETE)
- Architecture designed and approved by Codex
- 3-component design: semantic_bit package + GPU server + newdreamflow UI
- Security-first approach validated
- Documentation: `docs/ARCHITECTURE_FINAL.md`

### ✅ Phase 1: GPU Setup & Validation (COMPLETE)
- **Completed**: 2025-10-31 23:03 UTC
- **Duration**: ~2 hours
- **Result**: EXCEEDED ALL TARGETS

**Performance**:
- RTX 4070 Super validated in WSL2 Ubuntu 24.04
- Stable Diffusion v1.5: 2.62s average generation time
- Target: < 10s → **Achieved: 73.8% faster**
- Performance tier: **EXCELLENT**

**Environment**:
- GPU: NVIDIA GeForce RTX 4070 SUPER (12.9 GB VRAM)
- Platform: Windows WSL2 Ubuntu 24.04 LTS
- Python: 3.12.3
- PyTorch: 2.5.1+cu121
- CUDA: 12.1
- Model: Stable Diffusion v1.5 (float16)

**Test Location**: `~/gpu_test/` (in WSL2 Ubuntu)
**Model Cache**: `~/.cache/huggingface/hub/` (5.2GB)

**Documentation**:
- `docs/PHASE1_GPU_SETUP_COMPLETE.md` - Complete review (800+ lines)
- `docs/PHASE1_SESSION_HANDOFF.md` - Session notes
- `~/gpu_test/PHASE1_RESULTS.md` - Technical results (WSL2)

### 🔄 Phase 1 → Phase 2 Transition (WAITING)
- **Status**: Awaiting Codex review of Phase 1
- **Codex Questions**: See `docs/PHASE1_GPU_SETUP_COMPLETE.md` (bottom section)
- **Next Action**: Create `semantic_bit_gpu_server` repository

### ⏳ Phase 2: GPU Microservice (NEXT - Not Started)
- **Goal**: FastAPI server with Stable Diffusion
- **Duration**: 2-3 weeks estimated
- **Confidence**: HIGH (95%+) - Phase 1 resolved all technical risks

---

## Key Documentation

### Architecture (Codex Approved)
- **`docs/ARCHITECTURE_FINAL.md`** - Complete architecture (1200 lines)
- **`docs/ARCHITECTURE_CODEX_REVIEW.md`** - Codex review package
- **`docs/architecture_clean_separation.md`** - Component design

### Implementation Planning
- **`docs/IMPLEMENTATION_NEXT_STEPS.md`** - Phase-by-phase roadmap
- **`docs/ai_image_generation_plan.md`** - Image generation strategy
- **`docs/gpu_setup_options.md`** - Hardware options analysis

### Phase 1 Results
- **`docs/PHASE1_GPU_SETUP_COMPLETE.md`** - ⭐ Primary Phase 1 review
- **`docs/PHASE1_SESSION_HANDOFF.md`** - Session resume instructions
- **`docs/session_summary_2025-10-30.md`** - Planning session notes

### Other Important Docs
- **`docs/DOCUMENTATION_INDEX.md`** - Full documentation map
- **`docs/theory.md`** - Semantic Bit theory explanation
- **`docs/examples.md`** - Usage examples

---

## Codex Review Status

### Phase 1 Review (2025-11-01)
**Reviewer**: Codex
**Status**: Reviewed - See `docs/PHASE1_GPU_SETUP_COMPLETE.md` (Codex Alignment section)

**Codex Agreements**:
- ✅ Phase 1 complete and exceeds targets
- ✅ Ready for Phase 2
- ✅ Keep Stable Diffusion 1.5 for Phase 2
- ✅ FastAPI + request queue appropriate for ~2.6s inference
- ✅ Keep model loaded in VRAM, provide offline mode
- ✅ Basic health/metrics first, defer deep GPU telemetry

**Codex Clarifications**:
- ⚠️ CUDA version: Use 12.1 consistently (matches PyTorch cu121)
- ⚠️ Confirm driver versions: Windows 576.80 / WSL2 535.274.02
- ⚠️ Batch sizing: Target 2 images initially (safe on 12.9GB with fp16)

**Codex Questions & Answers**:
1. **Scheduler**: Phase 1 used default (PNDM). Codex recommends **DPMSolver++ 2M (Karras)** as default for Phase 2:
   - Settings: 24-28 steps, guidance_scale 7.0-7.5, fp16
   - Alternative: Euler Ancestral (30-40 steps) for classic SD 1.5 look
   - Action: Add scheduler benchmark in Phase 2 (20/24/28/32 steps)
2. **Repo**: ✅ Created at https://github.com/jblacketter/semantic_bit_gpu_server
3. **Version pinning**: ✅ Approved - will create `requirements.lock.txt`

**Codex Recommendations**:
- Use DPMSolver++ 2M with Karras sigmas as default scheduler
- Start with 2-image micro-batches (safe on 12.9GB fp16)
- Benchmark schedulers in Phase 2 to confirm optimal settings
- CUDA version unified to 12.1 (previous "12.9" was a typo)

---

## Important Context for Future Sessions

### When Resuming This Project

1. **Check Current Phase**: See "Current Status" section above
2. **Read Latest Documentation**: Start with phase-specific docs
3. **Review Codex Feedback**: Check `docs/PHASE1_GPU_SETUP_COMPLETE.md` bottom section
4. **Verify Environment**:
   - If Phase 2+: Work in `semantic_bit_gpu_server` repo
   - If documentation: Work in `semantic_bit_theory` repo

### WSL2 Environment (Windows)

**Access**:
```bash
# From Windows
wsl

# Navigate to test environment
cd ~/gpu_test
source venv/bin/activate
```

**Test Scripts Available**:
- `~/gpu_test/test_gpu.py` - GPU computation test
- `~/gpu_test/test_diffusion.py` - Image generation test
- `~/gpu_test/benchmark.py` - Performance benchmark

**Model Cache**: `~/.cache/huggingface/hub/` (5.2GB - already downloaded)

### Key Technical Decisions

1. **Python Version**: 3.12.3 (Ubuntu 24.04 default)
2. **CUDA Version**: 12.1 (not 11.8 from original plan)
3. **PyTorch**: 2.5.1+cu121 (install via `--index-url https://download.pytorch.org/whl/cu121`)
4. **Precision**: float16 for GPU efficiency (2x faster, half memory)
5. **Model**: Stable Diffusion v1.5 (`runwayml/stable-diffusion-v1-5`)

### Performance Baseline

- **Single image**: 3.24s (512x512, 50 steps)
- **Benchmark average**: 2.62s (3 images)
- **Target**: < 10s (achieved 73.8% faster)
- **VRAM usage**: ~7-8GB (out of 12.9GB available)
- **Scheduler**: PNDM (default)

---

## Next Actions (In Order)

### Immediate (Codex Review Complete ✅)
- [x] Phase 1 complete
- [x] Documentation created
- [x] Codex review requested
- [x] Codex review received (2025-11-01)
- [x] Codex questions answered
- [x] Repository created: https://github.com/jblacketter/semantic_bit_gpu_server

### Ready for Phase 2 Implementation
1. **Clone `semantic_bit_gpu_server` repository** ✅ DONE
   - URL: https://github.com/jblacketter/semantic_bit_gpu_server
   - Local location: `~/projects/semantic_bit_gpu_server`
   - Status: Already cloned and ready

2. **Set up Phase 2 project structure**
   ```
   semantic_bit_gpu_server/
   ├── README.md
   ├── server/
   │   ├── main.py              # FastAPI app
   │   ├── generator.py         # Stable Diffusion wrapper
   │   └── queue.py             # Request queue
   ├── requirements.txt
   ├── requirements.lock.txt    # Exact versions from Phase 1
   └── docs/
       └── setup.md
   ```

3. **Begin Phase 2 Implementation**
   - FastAPI server with `/generate` endpoint
   - Model loading and caching (keep model warm in VRAM)
   - Implement DPMSolver++ 2M (Karras) scheduler as default
   - Request queue management
   - Health check endpoint
   - Offline mode (work from cached model)
   - API documentation
   - Scheduler benchmark (20/24/28/32 steps comparison)

---

## Scheduler Configuration (Phase 2 Default)

**Codex Recommendation**: Use DPMSolver++ 2M with Karras sigmas

```python
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

# Set recommended scheduler
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config,
    algorithm_type="dpmsolver++",
    use_karras_sigmas=True
)

# Generate with recommended settings
image = pipe(
    prompt,
    num_inference_steps=28,      # 24-28 recommended
    guidance_scale=7.0,           # 7.0-7.5 recommended
    height=512,
    width=512
).images[0]
```

**Alternative (Classic SD 1.5 look)**:
```python
from diffusers import EulerAncestralDiscreteScheduler

pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
    pipe.scheduler.config
)
# Use 30-40 steps for this scheduler
```

**Phase 2 Task**: Benchmark 20/24/28/32 steps to confirm optimal default.

---

## Common Commands

### Check GPU Status (WSL2)
```bash
nvidia-smi
```

### Run Phase 1 Tests (WSL2)
```bash
cd ~/gpu_test
source venv/bin/activate
python test_gpu.py          # Quick GPU check
python test_diffusion.py    # Single image test
python benchmark.py         # Performance benchmark
```

### Recreate Phase 1 Environment (WSL2)
```bash
cd ~/gpu_test
python3 -m venv venv
source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install diffusers transformers accelerate safetensors
```

### Generate Documentation Summary
```bash
# From semantic_bit_theory repo root
ls -lh docs/PHASE*.md
cat docs/PHASE1_GPU_SETUP_COMPLETE.md
```

---

## Communication Channels

### With Codex
- **Reviews**: After each phase completion
- **Format**: Comprehensive review documents (see `docs/PHASE1_GPU_SETUP_COMPLETE.md`)
- **Questions**: Documented in review docs, answered in "Codex Alignment" section

### With Dan (User's Collaborator)
- **Phase 1**: Share GPU performance results (optional)
- **Phase 2**: Get input on API design
- **Phase 5-7**: Involve in security testing
- **Phase 8**: Grant Tailscale access for production use

---

## Project Timeline

| Phase | Duration | Status | Description |
|-------|----------|--------|-------------|
| 0 | 1 week | ✅ Complete | Planning & Architecture |
| 1 | 1-2 weeks | ✅ Complete | GPU Setup & Validation |
| 2 | 2-3 weeks | ⏳ Next | GPU Microservice (FastAPI) |
| 3 | 1-2 weeks | 📅 Planned | Extend semantic_bit package |
| 4 | 2-3 weeks | 📅 Planned | Integrate with newdreamflow |
| 5-7 | 3 weeks | 📅 Planned | Security testing & hardening |
| 8 | 1-2 weeks | 📅 Planned | Production deployment |

**Total**: 11-12 weeks
**Current**: Week 2 complete
**Progress**: ~15% complete

---

## Success Criteria

### Phase 1 (Complete ✅)
- [x] RTX 4070 Super detected and working
- [x] PyTorch CUDA support validated
- [x] Stable Diffusion generating images
- [x] Performance < 10s per image (achieved 2.62s)
- [x] Images valid and high quality

### Phase 2 (Next)
- [ ] FastAPI server running
- [ ] `/generate` endpoint functional
- [ ] Request queue handling concurrent requests
- [ ] Average response time < 5s (including queue)
- [ ] Model stays loaded in VRAM
- [ ] Offline mode works with cached model
- [ ] Basic health check endpoint
- [ ] API documentation complete

### Overall Project Success
- Complete implementation in 11-12 weeks
- Security validation passed
- Dan can access securely via Tailscale
- Cost under $20/month
- Users can generate visual slideshows
- Performance meets user expectations

---

## Important Notes

### Repository Switching
- **Now (Phase 1)**: Work in `semantic_bit_theory` for documentation
- **Phase 2**: Switch to `semantic_bit_gpu_server` for implementation
- **Phase 3**: Work in `semantic_bit` package repo
- **Phase 4**: Work in `newdreamflow` repo
- **Always**: Document in `semantic_bit_theory/docs/`

### Don't Confuse Projects
- `semantic_bit_theory` = Documentation hub (no implementation)
- `semantic_bit` = Python package (PyPI)
- `semantic_bit_gpu_server` = GPU microservice (to be created)
- `newdreamflow` = User interface (Gradio app)

### WSL2 vs Windows
- All GPU testing done in WSL2 Ubuntu
- Model cache in WSL2 filesystem
- Don't mix Windows and WSL2 paths

---

## Quick Reference Links

**GitHub Repositories**:
- semantic_bit_theory: https://github.com/antfriend/semantic_bit_theory (Dan's repo, you're collaborator)
- semantic_bit: https://github.com/jblacketter/semantic_bit (Your repo)
- semantic_bit_gpu_server: https://github.com/jblacketter/semantic_bit_gpu_server ✅ (Your repo, cloned to ~/projects/)
- newdreamflow: (Dan's or yours - verify ownership)

**External Resources**:
- HuggingFace Diffusers: https://huggingface.co/docs/diffusers
- Stable Diffusion v1.5: https://huggingface.co/runwayml/stable-diffusion-v1-5
- FastAPI: https://fastapi.tiangolo.com
- PyTorch: https://pytorch.org

---

## Troubleshooting

### GPU Not Detected in WSL2
```bash
# Update WSL2
wsl --update

# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Model Download Issues
```bash
# Clear cache and re-download
rm -rf ~/.cache/huggingface/hub/models--runwayml--stable-diffusion-v1-5

# Run download script
cd ~/gpu_test
source venv/bin/activate
python download_model.py
```

### Out of Memory
- Reduce inference steps: `num_inference_steps=30` (from 50)
- Reduce image size: `height=512, width=512` (already at minimum)
- Use float16: `torch_dtype=torch.float16` (already enabled)

---

## Version Information (Phase 1 Environment)

**Locked for reproducibility** (create `requirements.lock.txt` for Phase 2):

```
torch==2.5.1+cu121
torchvision==0.20.1+cu121
diffusers==0.35.2
transformers==4.57.1
accelerate==1.11.0
safetensors==0.6.2
huggingface-hub==0.36.0
```

**System**:
- OS: Ubuntu 24.04 LTS (WSL2)
- Python: 3.12.3
- CUDA: 12.1
- Driver: Windows 576.80 / WSL2 535.274.02

---

**Last Updated**: 2025-10-31
**Next Update**: After Phase 2 begins
**Maintained By**: Claude (AI assistant)
