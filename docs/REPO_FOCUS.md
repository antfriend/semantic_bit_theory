# Repository Focus and Organization

**Created**: 2025-11-01
**Purpose**: Clarify what belongs in each repository

---

## Repository Purposes

### semantic_bit_theory
**Focus**: semantic-bit pip package and GPU server infrastructure

**Contains**:
- ✅ `semantic_bit/` - Python package (Point-Line-Point encoding)
- ✅ `docs/` - Package theory, examples, GPU server docs
- ✅ `semantic_bit_gpu_server/` - FastAPI microservice (SIBLING, not part of package)

**Does NOT contain**:
- ❌ newdreamflow integration plans (moved to newdreamflow repo)
- ❌ Django application code
- ❌ Frontend implementation details

---

### newdreamflow
**Focus**: Django application using semantic-bit and GPU server

**Contains**:
- ✅ Django apps (dreams, things, patterns, etc.)
- ✅ Integration documentation (`docs/`)
- ✅ Migration plans (Phase D, E, F)
- ✅ Test scripts for GPU integration

**Dependencies**:
- semantic-bit package (from semantic_bit_theory)
- GPU server API (at http://localhost:8000)

---

### semantic_bit_gpu_server
**Focus**: Standalone FastAPI microservice for AI image generation

**Contains**:
- ✅ FastAPI application
- ✅ Stable Diffusion integration
- ✅ API documentation
- ✅ Smoke tests

**Used by**:
- newdreamflow (primary client)
- Any other service that needs image generation

---

## Current Work Location

**As of 2025-11-01**: All future work should be in **newdreamflow** repository

**Completed in semantic_bit_theory**:
- ✅ GPU server hardening (Phase A)
- ✅ GPU server testing (Phase B)
- ✅ newdreamflow audit (Phase C)

**Next work (in newdreamflow)**:
- ⏳ Semantic migration (Phase D)
- ⏳ GPU integration testing (Phase E)
- ⏳ Polish and documentation (Phase F)

---

## Documentation Location Guide

| Documentation Type | Location | Repository |
|-------------------|----------|------------|
| semantic-bit package docs | `semantic_bit_theory/semantic_bit/docs/` | semantic_bit_theory |
| semantic-bit theory | `semantic_bit_theory/docs/theory.md` | semantic_bit_theory |
| GPU server API docs | `semantic_bit_gpu_server/README.md` | semantic_bit_gpu_server |
| GPU server hardening | `semantic_bit_theory/docs/PHASE_A_COMPLETION_REPORT.md` | semantic_bit_theory |
| newdreamflow audit | `newdreamflow/docs/PHASE_C_NEWDREAMFLOW_AUDIT.md` | newdreamflow |
| newdreamflow migration | `newdreamflow/docs/PHASE_D_MIGRATION_PLAN.md` | newdreamflow |
| Integration overview | `newdreamflow/docs/README.md` | newdreamflow |

---

## Why This Organization?

### Separation of Concerns
- **semantic_bit_theory**: Reusable package + infrastructure
- **newdreamflow**: Application-specific integration
- **semantic_bit_gpu_server**: Standalone microservice

### Benefits
- ✅ Clear boundaries
- ✅ Easier to maintain
- ✅ Can use semantic-bit in other projects
- ✅ Can use GPU server from other clients
- ✅ newdreamflow docs stay with the app

### Tradeoff
- ⚠️ Must remember which repo to work in
- ⚠️ Multiple repositories to manage
- ✅ BUT: Better long-term organization

---

## Quick Reference: Where to Work

**Working on semantic encoding theory?** → semantic_bit_theory
**Working on GPU server API?** → semantic_bit_gpu_server
**Working on newdreamflow integration?** → newdreamflow
**Working on Django views/models?** → newdreamflow
**Working on migration plans?** → newdreamflow

---

**Current Focus**: newdreamflow (starting Phase D)
