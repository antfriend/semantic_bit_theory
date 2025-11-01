# Project Rules and Context (Cursor Rules)

Purpose
- Central place to track working rules, environment context, and project-wide decisions for all collaborators and AI assistants.
- Mirrors key agreements with Claude and Codex to keep alignment visible.

Scope
- Applies to the entire repository.
- For Codex/agents that prefer AGENTS.md, see the root AGENTS.md pointer (kept in sync with this file).

Environment & Repos
- OS: Windows 11 + WSL2 Ubuntu 24.04 LTS
- GPU: NVIDIA GeForce RTX 4070 SUPER (12.9 GB VRAM)
- Python: 3.12.3
- PyTorch: 2.5.1+cu121 (CUDA 12.1)
- GPU microservice repo: https://github.com/jblacketter/semantic_bit_gpu_server

Performance Baseline (Phase 1)
- Single image (512x512, 50 steps): 3.24s
- Benchmark average (3 images): 2.62s (73.8% faster than 10s target)
- Findings: No OOM, no corruption; stable and consistent.
- Source: docs/PHASE1_GPU_SETUP_COMPLETE.md (includes Quick Results Summary and details)

Architecture Direction (Agreed)
- Separate GPU microservice (FastAPI + async queue) for image generation.
- Keep Stable Diffusion 1.5 for Phase 2; revisit SDXL/2.1 later.
- Keep model loaded on GPU; add offline mode once model is cached.
- Basic health and metrics now; deeper GPU telemetry later.

Scheduler Defaults (Proposed and Adopted for Phase 2)
- Default: DPMSolver++ 2M (Karras), 24–28 steps, guidance_scale 7.0–7.5, fp16.
- Alternative: Euler Ancestral, 30–40 steps for the classic SD 1.5 look.
- Benchmark in Phase 2: compare 20/24/28/32 steps across both schedulers to confirm the final default.

Version Pinning
- Lock the validated versions for reproducibility:
  - torch==2.5.1+cu121, diffusers==0.35.2, transformers==4.57.1,
    accelerate==1.11.0, huggingface_hub==0.36.0, safetensors==0.6.2

Coding & Process Rules
- Keep changes minimal and focused; avoid unrelated refactors.
- Match existing code style; no license header changes unless requested.
- Prefer small, reviewable PRs; link changes back to docs when relevant.
- Update documentation alongside code changes when behavior or decisions change.

Docs to Consult
- docs/PHASE1_GPU_SETUP_COMPLETE.md (Phase 1 outcomes + Codex Alignment)
- docs/PHASE1_SESSION_HANDOFF.md (handoff, environment, scheduler defaults)
- README.md (Related Repositories)

Windows/WSL Notes
- Projects under WSL home (e.g., ~/projects/...) won’t appear under C:\ in Windows.
- Open WSL folders in Explorer with either:
  - In WSL: `explorer.exe .` (opens current WSL directory in Explorer), or
  - Explorer path: `\\wsl$\\Ubuntu-24.04\\home\\<user>\\projects\\...`
- If you need Windows-native visibility and indexing, put the project under `/mnt/c/Users/<user>/projects/...` (note: slightly slower for Linux I/O).

Ownership & Updates
- This file is source of truth for shared rules/context; keep in sync with AGENTS.md.
- When rules or defaults change, update here and reference in relevant docs.

