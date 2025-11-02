# semantic_bit_theory Documentation

This directory contains documentation for the semantic-bit pip package and GPU server infrastructure.

---

## Active Documentation

### GPU Server (semantic_bit_gpu_server)
- **[PHASE_A_COMPLETION_REPORT.md](PHASE_A_COMPLETION_REPORT.md)** - GPU server hardening (input validation, error handling, metadata headers)
- GPU server README: `~/projects/semantic_bit_gpu_server/README.md`
- GPU server docs: `~/projects/semantic_bit_gpu_server/docs/`

### semantic-bit Package
- **[theory.md](theory.md)** - Semantic bit theory fundamentals
- **[examples.md](examples.md)** - Usage examples
- **[FLEXIBLE_PATTERNS_GUIDE.md](FLEXIBLE_PATTERNS_GUIDE.md)** - v2.0 pattern guide
- Package README: `~/projects/semantic_bit_theory/semantic_bit/README.md`

### Project Status
- **[next_steps.md](next_steps.md)** - Current project status and next steps
- **[project_roadmap.md](project_roadmap.md)** - Long-term roadmap

---

## Archived Documentation

Historical and completed planning documents are in `archive/`:
- Integration planning (now in newdreamflow repo)
- Codex review history
- Old session handoffs

---

## Related Repositories

### newdreamflow (Django Application)
- **Location**: `~/projects/newdreamflow/`
- **Docs**: `~/projects/newdreamflow/docs/`
- **Purpose**: Django app that uses semantic-bit package and GPU server
- **Status**: Phase D ready (semantic migration)

### semantic_bit_gpu_server (FastAPI Microservice)
- **Location**: `~/projects/semantic_bit_gpu_server/`
- **URL**: `http://localhost:8000`
- **Purpose**: AI image generation microservice
- **Status**: Production-ready ✅ (32/32 tests passed)

---

## Quick Reference

### GPU Server Status
```bash
# Check if running
curl http://localhost:8000/health

# Start server
cd ~/projects/semantic_bit_gpu_server
source .venv/bin/activate
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### semantic-bit Package
```bash
# Install in development mode
cd ~/projects/semantic_bit_theory/semantic_bit
pip install -e .

# Run tests
pytest tests/
```

---

**Last Updated**: 2025-11-01
**Focus**: GPU server and pip package (newdreamflow integration moved to newdreamflow repo)
