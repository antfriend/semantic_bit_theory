# Implementation Plan: GPU Server → newdreamflow Integration

**Date**: 2025-11-01
**Status**: 📋 Planning Phase - Ready to Execute
**Codex Review**: ✅ Complete with detailed recommendations
**Contributors**: Jack, Claude, Codex

---

## Overview

This document provides a complete, step-by-step implementation plan based on Codex's comprehensive review. It organizes all recommendations into clear phases with specific tasks, acceptance criteria, and estimated timelines.

### Three-Phase Approach

1. **Phase A**: Harden GPU Server (implement Codex recommendations)
2. **Phase B**: Refactor newdreamflow to use semantic-bit pip package
3. **Phase C**: Integrate newdreamflow with GPU server

**Total Estimated Time**: 1-2 weeks
**Confidence**: High (95%+) - Clear requirements, validated architecture

---

## Phase A: Harden GPU Server (Before First Test)

**Goal**: Implement Codex's production-ready recommendations before testing
**Duration**: 2-3 hours
**Location**: `semantic_bit_gpu_server` repository (WSL2)

### Why Do This First?

From Codex's review, these changes:
- ✅ Prevent GPU OOM errors (input validation)
- ✅ Make debugging dramatically easier (response headers)
- ✅ Provide consistent error handling (error JSON format)
- ✅ Set up newdreamflow for success (proper API contract)

**Decision**: Implement ALL Codex recommendations before first test run

### Task Breakdown

#### A1: Update Request/Response Models (30 minutes)

**File**: `semantic_bit_gpu_server/server/main.py`

**Changes**:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class GenerateRequest(BaseModel):
    """Request model with Codex-recommended bounds"""
    prompt: str = Field(..., min_length=1, max_length=1000)
    num_inference_steps: int = Field(28, ge=5, le=60)
    guidance_scale: float = Field(7.0, ge=1.0, le=12.0)
    height: int = Field(512, ge=256, le=768)
    width: int = Field(512, ge=256, le=768)
    seed: Optional[int] = Field(None, ge=0, le=2**32-1)
    scheduler: Literal["dpmsolver++", "euler_ancestral"] = "dpmsolver++"

    @validator('height', 'width')
    def check_multiple_of_8(cls, v):
        if v % 8 != 0:
            raise ValueError('must be multiple of 8')
        return v


class ErrorResponse(BaseModel):
    """Consistent error response format"""
    error: str          # Error type: "InvalidParameter", "GenerationFailed", etc.
    code: int           # HTTP status code
    detail: str         # Human-readable message
    meta: Optional[dict] = None  # Additional context (field name, etc.)
```

**Acceptance Criteria**:
- ✅ Invalid inputs return 422 with clear JSON error
- ✅ Bounds enforced: steps [5,60], guidance [1.0,12.0], dims multiples of 8
- ✅ Max resolution 768x768 (safe on 12.9GB VRAM)

---

#### A2: Implement Error Response Handlers (20 minutes)

**File**: `semantic_bit_gpu_server/server/main.py`

**Changes**:

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI(title="Semantic Bit GPU Server")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with consistent format"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "code": 422,
            "detail": "Request validation failed",
            "meta": {"errors": exc.errors()}
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "code": 500,
            "detail": str(exc),
            "meta": None
        }
    )
```

**Status Codes**:
- 422: Pydantic validation errors (bounds/type)
- 400: Domain-level invalid values
- 503: Model not loaded/initializing
- 500: Unexpected failures
- 429: Rate limit (future)

**Acceptance Criteria**:
- ✅ All errors return consistent JSON format
- ✅ Clear, actionable error messages
- ✅ Proper HTTP status codes

---

#### A3: Add Response Metadata Headers (15 minutes)

**File**: `semantic_bit_gpu_server/server/main.py`

**Changes** to `/generate` endpoint:

```python
from fastapi import Response
import time

@app.post("/generate")
async def generate_image(request: GenerateRequest):
    """Generate image with metadata headers"""
    start_time = time.time()

    generator = get_generator()
    if not generator:
        return JSONResponse(
            status_code=503,
            content={
                "error": "ServiceUnavailable",
                "code": 503,
                "detail": "Model not loaded",
                "meta": None
            }
        )

    try:
        # Generate image
        image_bytes = generator.generate(
            prompt=request.prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            height=request.height,
            width=request.width,
            seed=request.seed,
            scheduler=request.scheduler
        )

        # Get actual seed used (if None was passed, generator creates one)
        actual_seed = generator.last_seed  # Assuming generator tracks this

        elapsed = time.time() - start_time

        # Build response with headers
        response = Response(content=image_bytes, media_type="image/png")
        response.headers["X-Seed"] = str(actual_seed)
        response.headers["X-Steps"] = str(request.num_inference_steps)
        response.headers["X-Guidance"] = str(request.guidance_scale)
        response.headers["X-Scheduler"] = request.scheduler
        response.headers["X-Device"] = generator.device
        response.headers["X-Generation-Time"] = f"{elapsed:.2f}s"
        response.headers["Cache-Control"] = "no-store"

        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "GenerationFailed",
                "code": 500,
                "detail": str(e),
                "meta": None
            }
        )
```

**Headers Added**:
- `X-Seed`: Actual seed used (for reproducibility)
- `X-Steps`: Number of inference steps
- `X-Guidance`: Guidance scale value
- `X-Scheduler`: Scheduler name
- `X-Device`: cuda/cpu
- `X-Generation-Time`: Elapsed time in seconds
- `Cache-Control`: `no-store` (prevent caching)

**Acceptance Criteria**:
- ✅ All successful responses include metadata headers
- ✅ Headers contain correct values
- ✅ Cache-Control prevents unintended caching

---

#### A4: Update Generator to Track Seed (10 minutes)

**File**: `semantic_bit_gpu_server/server/generator.py`

**Changes**:

```python
class ImageGenerator:
    def __init__(self, ...):
        # ... existing init ...
        self.last_seed = None  # Track last used seed

    def generate(self, ..., seed: Optional[int] = None, ...):
        """Generate image and track seed"""
        # Generate seed if not provided
        if seed is None:
            import random
            seed = random.randint(0, 2**32 - 1)

        self.last_seed = seed  # Track it

        # Use seed in generation
        generator_obj = torch.Generator(device=self.device).manual_seed(seed)

        # ... rest of generation with generator=generator_obj ...
```

**Acceptance Criteria**:
- ✅ Seed is generated if not provided
- ✅ Last seed is accessible to endpoint
- ✅ Seed is used consistently in generation

---

#### A5: Add Optional API Key Support (15 minutes)

**Files**:
- `semantic_bit_gpu_server/server/config.py`
- `semantic_bit_gpu_server/server/main.py`

**Config Addition**:

```python
# config.py
class Settings(BaseSettings):
    # ... existing settings ...
    API_KEY: Optional[str] = None  # Optional bearer token
```

**Middleware Addition**:

```python
# main.py
from fastapi import Header, HTTPException
from typing import Optional

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """Optional API key verification"""
    if not settings.API_KEY:
        return  # No auth required if not configured

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    token = authorization.replace("Bearer ", "")
    if token != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

# Add dependency to protected endpoints
@app.post("/generate", dependencies=[Depends(verify_api_key)])
async def generate_image(...):
    ...
```

**Acceptance Criteria**:
- ✅ API key is optional (off by default)
- ✅ When enabled, requires valid Bearer token
- ✅ Returns 401 for invalid/missing auth

---

#### A6: Update README and Documentation (30 minutes)

**Files**:
- `semantic_bit_gpu_server/README.md`
- `semantic_bit_gpu_server/.env.example`

**README Sections to Add**:
1. API Reference (endpoints, parameters, responses)
2. Error Handling (error format, status codes)
3. Response Headers (metadata fields)
4. Authentication (optional API key)
5. Testing Guide (curl examples)

**Example curl with headers**:

```bash
# Test with header inspection
curl -i -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{
    "prompt": "a small cactus in a terracotta pot",
    "num_inference_steps": 28,
    "guidance_scale": 7.0
  }' \
  -o test_image.png

# Check headers in response
# Should see X-Seed, X-Steps, X-Guidance, etc.
```

**.env.example Update**:

```bash
# Optional API key for basic authentication
# Leave empty to disable auth
GPU_SERVER_API_KEY=

# Maximum resolution (default 768, adjust based on VRAM)
MAX_RESOLUTION=768
```

**Acceptance Criteria**:
- ✅ README documents all endpoints with examples
- ✅ Error format documented with examples
- ✅ Response headers explained
- ✅ curl test examples provided

---

### Phase A Summary

**Total Time**: ~2-3 hours
**Files Modified**: 4 files
- `server/main.py` (request/response models, error handlers, headers)
- `server/generator.py` (seed tracking)
- `server/config.py` (API key setting)
- `README.md` + `.env.example` (documentation)

**Lines Added**: ~200-300 lines
**Complexity**: Low-Medium (straightforward additions)

**Verification Checklist**:
- [ ] All Pydantic models updated with bounds
- [ ] Error handlers implemented for all endpoints
- [ ] Response headers added to `/generate`
- [ ] Seed tracking working in generator
- [ ] Optional API key auth implemented
- [ ] README fully documented
- [ ] `.env.example` updated

---

## Phase B: Test GPU Server (Validation)

**Goal**: Verify GPU server works correctly with all new features
**Duration**: 1-2 hours
**Location**: WSL2 Ubuntu

### Task Breakdown

#### B1: Setup and Install (10 minutes)

```bash
cd ~/projects/semantic_bit_gpu_server
python3 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA
pip install --index-url https://download.pytorch.org/whl/cu121 \
  torch==2.5.1+cu121 torchvision==0.20.1+cu121

# Install other dependencies
pip install -r requirements.lock.txt
```

**Acceptance Criteria**:
- ✅ Virtual environment created
- ✅ All dependencies installed
- ✅ No import errors

---

#### B2: Start Server (5 minutes)

```bash
# Bind to 0.0.0.0 for Windows access
uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 1
```

**Expected Output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Loading model: runwayml/stable-diffusion-v1-5
INFO:     Model loaded successfully on cuda
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Acceptance Criteria**:
- ✅ Server starts without errors
- ✅ Model loads successfully
- ✅ Accessible from Windows at `http://localhost:8000`

---

#### B3: Run Test Checklist (30 minutes)

From Codex's recommendations:

**Test 1: Health Check**
```bash
curl -s http://localhost:8000/health | jq .
```

**Expected**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "runwayml/stable-diffusion-v1-5",
  "device": "cuda",
  "config": {
    "default_steps": 28,
    "default_guidance_scale": 7.0,
    "default_scheduler": "dpmsolver++"
  }
}
```

**Test 2: Valid Generation with Headers**
```bash
curl -i -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{
    "prompt": "a small cactus in a terracotta pot, studio lighting",
    "num_inference_steps": 28,
    "guidance_scale": 7.0
  }' \
  -o test_valid.png
```

**Expected**:
- Status: 200 OK
- Content-Type: image/png
- Headers: X-Seed, X-Steps, X-Guidance, X-Scheduler, X-Device, X-Generation-Time
- File: Valid PNG image

**Verify**:
```bash
file test_valid.png  # Should say "PNG image data"
```

**Test 3: Invalid Parameters (Bounds Check)**
```bash
# Invalid steps (too low)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"test","num_inference_steps":2}' | jq .
```

**Expected**:
```json
{
  "error": "ValidationError",
  "code": 422,
  "detail": "Request validation failed",
  "meta": {
    "errors": [
      {
        "loc": ["body", "num_inference_steps"],
        "msg": "ensure this value is greater than or equal to 5",
        "type": "value_error.number.not_ge"
      }
    ]
  }
}
```

**Test 4: Invalid Dimensions (Not Multiple of 8)**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"test","height":513}' | jq .
```

**Expected**: 422 error with "must be multiple of 8"

**Test 5: API Key (if enabled)**
```bash
# Set API_KEY in .env first
export API_KEY="test_key_123"

# Without auth - should fail
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"test"}' | jq .

# Expected: 401 Unauthorized

# With auth - should succeed
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_key_123" \
  --data '{"prompt":"test"}' \
  -o test_auth.png
```

**Test 6: Seed Reproducibility**
```bash
# Generate with seed
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"a red apple","seed":42}' \
  -o apple1.png

# Generate again with same seed
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"a red apple","seed":42}' \
  -o apple2.png

# Compare
diff apple1.png apple2.png  # Should be identical
```

**Test 7: Scheduler Selection**
```bash
# DPMSolver++ (default)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"sunset","scheduler":"dpmsolver++"}' \
  -o sunset_dpm.png

# Euler Ancestral
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"sunset","scheduler":"euler_ancestral"}' \
  -o sunset_euler.png
```

**Test 8: Performance Baseline**
```bash
# Measure warm request time (model already loaded)
time curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data '{"prompt":"test performance"}' \
  -o perf_test.png

# Expected: ~2.6-3.0 seconds for warm request
```

**Acceptance Criteria**:
- ✅ All tests pass
- ✅ Errors return proper JSON format
- ✅ Headers present and correct
- ✅ Images are valid PNGs
- ✅ Performance meets expectations (~3s)

---

#### B4: Run Scheduler Benchmark (Optional, 30 minutes)

```bash
python scripts/benchmark_schedulers.py
```

**Expected Output**: Performance comparison report

**Acceptance Criteria**:
- ✅ Benchmark completes without errors
- ✅ Results validate Codex recommendations (DPMSolver++ @ 28 steps)

---

#### B5: Document Results (15 minutes)

Create: `semantic_bit_gpu_server/docs/TESTING_RESULTS.md`

**Contents**:
- Test execution date/time
- All test results (pass/fail)
- Performance metrics
- Any issues discovered
- Screenshots of generated images (optional)

**Acceptance Criteria**:
- ✅ All tests documented
- ✅ Results shared with Codex (if needed)
- ✅ Any issues noted for fixing

---

### Phase B Summary

**Total Time**: 1-2 hours
**Outcome**: Validated, production-ready GPU server

**Success Criteria**:
- ✅ Server starts and runs stably
- ✅ All API endpoints working
- ✅ Error handling correct
- ✅ Headers present
- ✅ Performance acceptable
- ✅ Ready for newdreamflow integration

---

## Phase C: Audit newdreamflow (Discovery)

**Goal**: Understand current newdreamflow implementation before making changes
**Duration**: 1-2 hours
**Location**: `~/projects/newdreamflow/`

### Task Breakdown

#### C1: Examine Current Structure (30 minutes)

**Questions to Answer**:
1. What Django apps exist?
2. Where is semantic encoding logic?
3. What dependencies are installed?
4. Are there existing models for semantic data?
5. What's the current user flow?

**Commands**:
```bash
cd ~/projects/newdreamflow

# Check Django apps
ls apps/

# Check requirements
cat requirements.txt

# Check models
find . -name "models.py" -exec grep -l "semantic\|encode\|bit" {} \;

# Check views
find . -name "views.py" -exec grep -l "semantic\|encode\|bit" {} \;

# Check settings
cat newdreamflow/settings.py | grep -i semantic
```

**Document Findings** in `semantic_bit_theory/docs/NEWDREAMFLOW_AUDIT.md`

---

#### C2: Identify Semantic Encoding Implementation (30 minutes)

**Look For**:
- Custom encoding functions
- Imports from old semantic_bit code
- Point/Line term extraction logic
- Pattern type handling

**Document**:
- File locations
- Function signatures
- Dependencies
- Differences from current semantic-bit pip package

---

#### C3: Identify Integration Points (20 minutes)

**Questions**:
1. Where would GPU server calls fit in?
2. What views/endpoints need image generation?
3. How are results currently displayed?
4. What database models need updating?

---

#### C4: Create Migration Plan (20 minutes)

Based on findings, document:
1. Files to modify
2. Code to remove (old encoding)
3. Code to add (pip package usage)
4. Database migrations needed
5. Breaking changes to handle

**Output**: `semantic_bit_theory/docs/NEWDREAMFLOW_MIGRATION_PLAN.md`

---

### Phase C Summary

**Total Time**: 1-2 hours
**Outcome**: Complete understanding of newdreamflow current state

**Deliverables**:
- `NEWDREAMFLOW_AUDIT.md` - Current state documentation
- `NEWDREAMFLOW_MIGRATION_PLAN.md` - Step-by-step migration plan

---

## Phase D: Refactor newdreamflow to Use semantic-bit Pip

**Goal**: Replace custom semantic encoding with semantic-bit pip package
**Duration**: 2-4 hours
**Location**: `~/projects/newdreamflow/`

### Task Breakdown

#### D1: Update Dependencies (10 minutes)

**File**: `newdreamflow/requirements.txt`

**Add**:
```txt
semantic-bit>=0.2.0
requests>=2.31.0
pillow>=10.0.0
```

**Install**:
```bash
cd ~/projects/newdreamflow
source .venv/bin/activate
pip install -r requirements.txt
```

---

#### D2: Replace Encoding Logic (1-2 hours)

**For Each File Using Old Encoding**:

**Before** (hypothetical):
```python
from .utils.semantic_encoder import encode_text, extract_points

def process_text(text):
    result = encode_text(text, pattern="point_line")
    points = extract_points(result)
    return points
```

**After**:
```python
from semantic_bit import encode

def process_text(text):
    result = encode(text, pattern_type="point_line")
    # New format matches semantic-bit pip package
    return result
```

**Files to Update** (based on audit):
- TBD from Phase C audit

---

#### D3: Update Database Models (if needed) (30-60 minutes)

**Example Migration**:

If models store semantic data differently:

```python
# Create migration
python manage.py makemigrations

# Review migration
# Edit if needed

# Apply migration
python manage.py migrate
```

---

#### D4: Update Views/Templates (1 hour)

Update any views that:
- Call encoding functions
- Display semantic data
- Process encoding results

**Ensure**:
- Correct API usage
- Proper error handling
- Same user experience

---

#### D5: Test Refactored Code (30 minutes)

```bash
# Run Django tests
python manage.py test

# Manual testing in browser
python manage.py runserver
# Test encoding flow end-to-end
```

**Acceptance Criteria**:
- ✅ All tests pass
- ✅ Encoding works correctly
- ✅ No regressions in functionality
- ✅ Same user experience

---

### Phase D Summary

**Total Time**: 2-4 hours
**Outcome**: newdreamflow using semantic-bit pip package cleanly

**Success Criteria**:
- ✅ No custom encoding logic (uses pip package)
- ✅ All functionality preserved
- ✅ Tests passing
- ✅ Ready for GPU integration

---

## Phase E: Integrate GPU Server into newdreamflow

**Goal**: Wire newdreamflow to call GPU server for image generation
**Duration**: 3-5 hours
**Location**: `~/projects/newdreamflow/`

### Task Breakdown

#### E1: Create GPU Service Module (1 hour)

**File**: `newdreamflow/services/gpu_service.py`

**Implementation** (from Codex's example):

```python
import os
import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class GPUServerClient:
    """Client for semantic_bit_gpu_server API with retries and error handling"""

    def __init__(self,
                 base_url: Optional[str] = None,
                 timeout: int = 30,
                 api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv("GPU_SERVER_URL", "http://localhost:8000")
        self.timeout = int(os.getenv("GPU_SERVER_TIMEOUT", str(timeout)))
        self.api_key = api_key or os.getenv("GPU_SERVER_API_KEY")

        # Configure retries with backoff
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def health(self) -> Dict[str, Any]:
        """Check GPU server health"""
        r = self.session.get(
            f"{self.base_url}/health",
            headers=self._headers(),
            timeout=5
        )
        r.raise_for_status()
        return r.json()

    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate image from prompt.

        Returns:
            {
                "image_bytes": bytes,  # PNG data
                "meta": {
                    "seed": str,
                    "steps": str,
                    "scheduler": str,
                    "device": str,
                    "generation_time": str
                }
            }

        Raises:
            RuntimeError: If generation fails
            requests.exceptions.RequestException: If network/server issues
        """
        payload = {
            "prompt": prompt,
            **kwargs,
        }
        headers = {"Content-Type": "application/json", **self._headers()}

        r = self.session.post(
            f"{self.base_url}/generate",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )

        if r.status_code != 200:
            # Expect JSON error shape
            try:
                err = r.json()
            except Exception:
                r.raise_for_status()
            raise RuntimeError(
                f"GPU server error {err.get('code')}: "
                f"{err.get('error')} - {err.get('detail')}"
            )

        # Extract PNG and metadata from headers
        png_bytes = r.content
        meta = {
            "seed": r.headers.get("X-Seed"),
            "steps": r.headers.get("X-Steps"),
            "scheduler": r.headers.get("X-Scheduler"),
            "device": r.headers.get("X-Device"),
            "generation_time": r.headers.get("X-Generation-Time"),
        }

        return {
            "image_bytes": png_bytes,
            "meta": meta,
        }
```

**Tests**: `newdreamflow/services/tests/test_gpu_service.py`

```python
import unittest
from unittest.mock import Mock, patch
from services.gpu_service import GPUServerClient


class TestGPUServerClient(unittest.TestCase):
    def test_health_check(self):
        # Mock health check
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value.json.return_value = {"status": "healthy"}
            client = GPUServerClient()
            result = client.health()
            self.assertEqual(result["status"], "healthy")

    def test_generate_image(self):
        # Mock image generation
        with patch('requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'fake_png_data'
            mock_response.headers = {
                "X-Seed": "12345",
                "X-Steps": "28",
                "X-Scheduler": "dpmsolver++",
                "X-Device": "cuda"
            }
            mock_post.return_value = mock_response

            client = GPUServerClient()
            result = client.generate_image("test prompt")

            self.assertEqual(result["image_bytes"], b'fake_png_data')
            self.assertEqual(result["meta"]["seed"], "12345")
```

---

#### E2: Update Django Settings (15 minutes)

**File**: `newdreamflow/settings.py`

**Add**:
```python
# GPU Server Configuration
GPU_SERVER_URL = os.getenv('GPU_SERVER_URL', 'http://localhost:8000')
GPU_SERVER_TIMEOUT = int(os.getenv('GPU_SERVER_TIMEOUT', '30'))
GPU_SERVER_ENABLED = os.getenv('GPU_SERVER_ENABLED', 'true').lower() == 'true'
GPU_SERVER_API_KEY = os.getenv('GPU_SERVER_API_KEY', None)
```

**File**: `newdreamflow/.env`

**Add**:
```bash
GPU_SERVER_URL=http://localhost:8000
GPU_SERVER_TIMEOUT=30
GPU_SERVER_ENABLED=true
# GPU_SERVER_API_KEY=your_key_here
```

---

#### E3: Create Image Generation View (1-2 hours)

**File**: `newdreamflow/apps/generator/views.py` (or appropriate app)

**Example Implementation**:

```python
from django.http import HttpResponse, JsonResponse
from django.views import View
from services.gpu_service import GPUServerClient
import logging

logger = logging.getLogger(__name__)


class GenerateImageView(View):
    """Generate image from semantic bit prompt"""

    def post(self, request):
        # Get prompt from request
        prompt = request.POST.get('prompt')
        if not prompt:
            return JsonResponse({
                'error': 'missing_prompt',
                'detail': 'Prompt is required'
            }, status=400)

        # Get optional parameters
        num_steps = int(request.POST.get('num_steps', 28))
        guidance = float(request.POST.get('guidance', 7.0))

        # Call GPU server
        client = GPUServerClient()
        try:
            result = client.generate_image(
                prompt=prompt,
                num_inference_steps=num_steps,
                guidance_scale=guidance
            )

            # Log metadata
            logger.info(f"Generated image: {result['meta']}")

            # Return PNG
            response = HttpResponse(
                result["image_bytes"],
                content_type="image/png"
            )

            # Add metadata to response headers (optional)
            response['X-Seed'] = result['meta'].get('seed', '')
            response['X-Generation-Time'] = result['meta'].get('generation_time', '')

            return response

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            # Graceful degradation
            return JsonResponse({
                'error': 'generation_failed',
                'detail': str(e)
            }, status=502)
```

**URL Configuration**:

```python
# urls.py
from django.urls import path
from apps.generator.views import GenerateImageView

urlpatterns = [
    # ... existing patterns ...
    path('api/generate-image/', GenerateImageView.as_view(), name='generate_image'),
]
```

---

#### E4: Update Frontend (1-2 hours)

**File**: Template file (TBD based on audit)

**Add Image Display**:

```html
<div id="generated-image-container">
    <h3>Generated Image</h3>
    <img id="generated-image" src="" alt="Generated image" style="display:none;">
    <div id="image-loading" style="display:none;">Generating image...</div>
    <div id="image-error" style="display:none;"></div>
</div>

<script>
function generateImage(prompt) {
    const container = document.getElementById('generated-image');
    const loading = document.getElementById('image-loading');
    const error = document.getElementById('image-error');

    // Show loading
    container.style.display = 'none';
    loading.style.display = 'block';
    error.style.display = 'none';

    // Call backend
    fetch('/api/generate-image/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `prompt=${encodeURIComponent(prompt)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Generation failed');
        }
        return response.blob();
    })
    .then(blob => {
        // Display image
        const url = URL.createObjectURL(blob);
        container.src = url;
        container.style.display = 'block';
        loading.style.display = 'none';
    })
    .catch(err => {
        // Show error
        error.textContent = `Error: ${err.message}`;
        error.style.display = 'block';
        loading.style.display = 'none';
    });
}
</script>
```

---

#### E5: Add Image Storage (Optional, 1 hour)

**If images should be persisted**:

**Model**:
```python
# models.py
from django.db import models

class GeneratedImage(models.Model):
    prompt = models.TextField()
    image = models.ImageField(upload_to='generated/')
    seed = models.BigIntegerField(null=True)
    steps = models.IntegerField(null=True)
    scheduler = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

**Migration**:
```bash
python manage.py makemigrations
python manage.py migrate
```

**Update View to Save**:
```python
from apps.generator.models import GeneratedImage
from django.core.files.base import ContentFile

# In GenerateImageView after generation:
image_obj = GeneratedImage.objects.create(
    prompt=prompt,
    seed=int(result['meta'].get('seed', 0)),
    steps=int(result['meta'].get('steps', 0)),
    scheduler=result['meta'].get('scheduler', '')
)
image_obj.image.save(
    f'generated_{image_obj.id}.png',
    ContentFile(result['image_bytes']),
    save=True
)
```

---

#### E6: Test Integration End-to-End (1 hour)

**Test Flow**:
1. Start GPU server (WSL2)
2. Start Django development server
3. Navigate to newdreamflow in browser
4. Enter text for semantic encoding
5. Generate semantic bits
6. Generate image from semantic bit
7. Verify image displays correctly

**Acceptance Criteria**:
- ✅ newdreamflow can call GPU server
- ✅ Images generate successfully
- ✅ Images display in browser
- ✅ Errors handled gracefully
- ✅ Metadata tracked correctly

---

### Phase E Summary

**Total Time**: 3-5 hours
**Outcome**: Complete integration of GPU server into newdreamflow

**Files Created**:
- `services/gpu_service.py` - GPU server client
- `services/tests/test_gpu_service.py` - Tests
- `apps/generator/views.py` - Image generation view
- `apps/generator/models.py` - Image storage model (optional)
- Template updates for image display

**Success Criteria**:
- ✅ End-to-end flow working
- ✅ GPU server integration complete
- ✅ Error handling robust
- ✅ User can generate and view images

---

## Phase F: Polish and Documentation

**Goal**: Clean up, document, and prepare for user testing
**Duration**: 2-3 hours

### Task Breakdown

#### F1: Error Handling Review (30 minutes)

- Review all error paths
- Ensure user-friendly messages
- Add logging where needed
- Test error scenarios

---

#### F2: Performance Optimization (30 minutes)

- Check for N+1 queries
- Add caching where appropriate
- Optimize image delivery
- Test with multiple concurrent requests

---

#### F3: Documentation (1 hour)

**Create**:
- `newdreamflow/docs/GPU_INTEGRATION.md` - Integration guide
- Update `newdreamflow/README.md` - Setup instructions
- Create user guide for image generation feature

---

#### F4: User Testing Preparation (30 minutes)

- Create test account
- Prepare test prompts
- Document expected behavior
- Create feedback form/checklist

---

### Phase F Summary

**Total Time**: 2-3 hours
**Outcome**: Production-ready integration with documentation

---

## Overall Timeline

| Phase | Duration | Dependencies | Status |
|-------|----------|--------------|--------|
| A: Harden GPU Server | 2-3 hours | None | 📋 Ready to start |
| B: Test GPU Server | 1-2 hours | Phase A | ⏳ Blocked by A |
| C: Audit newdreamflow | 1-2 hours | None | ⏳ Can run parallel with A |
| D: Refactor newdreamflow | 2-4 hours | Phase C | ⏳ Blocked by C |
| E: Integrate GPU Server | 3-5 hours | Phases B, D | ⏳ Blocked by B+D |
| F: Polish & Docs | 2-3 hours | Phase E | ⏳ Blocked by E |

**Total Sequential Time**: 11-19 hours (1.5-2.5 days of focused work)
**With Parallelization**: 9-17 hours (Phases A+C can run together)

---

## Decision Log

### Decisions Made

1. ✅ **Implement all Codex recommendations before testing** - Prevents rework
2. ✅ **Maximum resolution 768x768** - Safe for 12.9GB VRAM with fp16
3. ✅ **Optional API key auth** - Simple bearer token until Tailscale
4. ✅ **Response metadata in headers** - Non-breaking, great for debugging
5. ✅ **Retry logic in client** - Graceful handling of network issues

### Decisions Pending

1. ⚠️ **Image storage strategy** - Database, filesystem, or external?
2. ⚠️ **Image caching** - Cache by prompt hash? TTL?
3. ⚠️ **Rate limiting** - Per user? Global? Deferred to later?
4. ⚠️ **Batch generation** - Single vs multiple images per request?

### Recommendations

- **Start with**: No caching, no rate limiting, single image per request
- **Add later**: Based on actual usage patterns
- **Reason**: Don't over-engineer until we see real needs

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GPU server OOM | Low | High | ✅ Strict input bounds (max 768x768) |
| Network issues WSL2↔Windows | Medium | Medium | ✅ Retry logic, clear error messages |
| Breaking changes in semantic-bit | Low | High | ✅ Pin version, test thoroughly |
| Performance degradation | Low | Medium | ✅ Benchmark before/after |
| User confusion | Medium | Low | ✅ Clear UI, good error messages |

---

## Success Criteria

### Technical Success

- ✅ GPU server passes all tests
- ✅ Error handling robust and consistent
- ✅ Response times meet targets (<5s)
- ✅ No regressions in newdreamflow functionality
- ✅ Clean, maintainable code

### User Success

- ✅ User can generate images from text
- ✅ Images display correctly
- ✅ Errors are understandable
- ✅ Performance feels responsive
- ✅ Feature is discoverable and usable

### Project Success

- ✅ All Codex recommendations implemented
- ✅ Architecture clean and scalable
- ✅ Documentation complete
- ✅ Ready for next phase (security/Tailscale)

---

## Next Actions

### Immediate (This Session)

1. **Review this plan with Codex** - Get final approval
2. **Answer pending questions** - Image storage, caching, etc.
3. **Prepare workspace** - Ensure all repos ready

### After Approval

4. **Start Phase A** - Implement GPU server hardening (~2-3 hours)
5. **Start Phase C in parallel** - Audit newdreamflow (~1-2 hours)
6. **Continue sequentially** - Phases B → D → E → F

---

## Questions for Codex

### High Priority

1. **Image storage**: Recommend database, filesystem, or defer?
2. **Max resolution**: Confirm 768x768 is safe? Or can we go 1024x1024?
3. **Rate limiting**: Implement now or defer to Phase 3?

### Medium Priority

4. **Caching strategy**: Worth implementing early or wait for usage data?
5. **Batch generation**: Should we support multiple images per request initially?
6. **Monitoring**: What metrics should we track from day one?

### Low Priority

7. **Docker**: Should we containerize GPU server now or later?
8. **CI/CD**: Set up automated testing now or defer?

---

**Status**: 📋 Plan complete, awaiting final review
**Next**: Get Codex approval, then execute
**Timeline**: 1.5-2.5 days of focused implementation
**Confidence**: Very High (98%) - Clear requirements, proven architecture, detailed plan

---

**Document Created**: 2025-11-01
**Authors**: Claude (with Codex guidance)
**For**: Jack (implementation) + Codex (review)
**Purpose**: Comprehensive implementation roadmap for GPU server → newdreamflow integration
