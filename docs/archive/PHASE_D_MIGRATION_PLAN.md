# Phase D: newdreamflow Migration Plan

**Date**: 2025-11-01
**Prerequisites**: Phase C audit complete
**Estimated Duration**: 4-6 hours
**Risk Level**: Medium

---

## Overview

This phase replaces the spaCy-only semantic analysis in newdreamflow with the proper semantic-bit v2.0 package implementation. The migration maintains backward compatibility and allows gradual rollout via feature flags.

**Scope**:
- Update semantic_service.py in both `dreams` and `things` apps
- Modify views to use new semantic-bit API
- Update templates for Point/Line highlighting (vs verb/noun)
- Add feature flag for gradual rollout
- Optional: Data migration script

**Out of Scope**:
- GPU integration (already done, Phase E will test)
- Frontend redesign (keep existing UX, just update colors)
- Database schema changes (JSONField is already flexible)

---

## Pre-Flight Checklist

Before starting Phase D, verify:

- [ ] Phase C audit reviewed and understood
- [ ] semantic_bit_theory repo up to date
- [ ] semantic-bit pip package built and tested
- [ ] newdreamflow virtual environment activated
- [ ] Database backed up (optional but recommended)
- [ ] Feature branch created: `feature/semantic-bit-v2`

---

## Step 1: Environment Setup (15 minutes)

### 1.1 Activate newdreamflow Environment

```bash
cd ~/projects/newdreamflow
source .venv/bin/activate
```

### 1.2 Verify Current semantic_bit Installation

```bash
pip show semantic_bit
# Should show: Version: 2.0.0 (or similar)
```

### 1.3 Install/Update semantic_bit

If not installed or outdated:

```bash
cd ~/projects/semantic_bit_theory/semantic_bit
pip install -e .
```

Verify:

```bash
python -c "import semantic_bit; print(semantic_bit.__version__)"
# Expected: 2.0.0
```

### 1.4 Test Import

```bash
python -c "from semantic_bit import encode_text_to_sb; print('OK')"
# Expected: OK
```

---

## Step 2: Fix .env Configuration (5 minutes)

### 2.1 Fix Duplicate GPU_SERVER_URL

**File**: `/home/jblac/projects/newdreamflow/.env`

**Issue**: Line 26 has malformed duplicate

**Current (lines 24-27)**:
```bash
# Security settings (for production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=FalseGPU_SERVER_URL=http://localhost:8000
```

**Fixed (lines 24-26)**:
```bash
# Security settings (for production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

**Action**: Remove everything after `=False` on line 26 (the duplicate `GPU_SERVER_URL`)

### 2.2 Add Feature Flag

**File**: `/home/jblac/projects/newdreamflow/.env`

Add at end:

```bash
# Semantic Bit Feature Flag
# Set to 'true' to enable semantic-bit v2.0 encoding
# Set to 'false' to keep legacy spaCy encoding
FEATURE_SEMANTIC_V2=true
```

### 2.3 Update .env.example

**File**: `/home/jblac/projects/newdreamflow/.env.example`

Add the same feature flag documentation.

---

## Step 3: Update Django Settings (10 minutes)

### 3.1 Add Feature Flag to Settings

**File**: `/home/jblac/projects/newdreamflow/newdreamflow/settings.py`

**Location**: After line 63 (after `FEATURE_ALGOLIA_ONLY`)

**Add**:
```python
# Feature flags
FEATURE_GROUPS = os.getenv('FEATURE_GROUPS', 'false').lower() == 'true'
FEATURE_ALGOLIA_ONLY = os.getenv('FEATURE_ALGOLIA_ONLY', 'false').lower() == 'true'
# NEW: Semantic Bit v2.0 encoding
FEATURE_SEMANTIC_V2 = os.getenv('FEATURE_SEMANTIC_V2', 'true').lower() == 'true'
```

**Note**: Default is `'true'` for new implementation. Set to `'false'` to rollback.

---

## Step 4: Update semantic_service.py - Dreams App (45 minutes)

### 4.1 Backup Current File

```bash
cp apps/dreams/services/semantic_service.py apps/dreams/services/semantic_service.py.bak
```

### 4.2 Replace Implementation

**File**: `/home/jblac/projects/newdreamflow/apps/dreams/services/semantic_service.py`

**Strategy**: Keep the same class interface, change implementation

**New Implementation** (see full code below):

```python
import semantic_bit
from typing import Dict, List, Tuple
from django.utils.html import format_html, mark_safe
from django.conf import settings


class SemanticService:
    """Service for semantic bit theory analysis of text (v2.0)."""

    def __init__(self):
        self.version = "2.0"
        self.legacy_mode = not getattr(settings, 'FEATURE_SEMANTIC_V2', True)

        # Load spaCy only if legacy mode
        if self.legacy_mode:
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
                self.model_loaded = True
            except Exception as e:
                print(f"Warning: spaCy model not loaded. Error: {e}")
                self.nlp = None
                self.model_loaded = False

    def extract_semantic_bits(self, text: str) -> Dict:
        """
        Extract semantic bits from text using semantic-bit v2.0.

        Falls back to legacy spaCy mode if FEATURE_SEMANTIC_V2=false.

        Returns:
            Dict compatible with both v1 (spaCy) and v2 (semantic-bit) formats
        """
        if not text:
            return self._empty_result()

        if self.legacy_mode:
            return self._extract_legacy(text)

        try:
            # Use semantic-bit v2.0
            result = semantic_bit.encode_text_to_sb(text)

            # Return result as dict (already JSON-serializable)
            return {
                'version': '2.0',
                'document': result,
                'text': text,
                'sentence_count': len(result.get('sentences', [])),
                'pattern_types': result.get('patterns', []),
            }
        except Exception as e:
            print(f"Error in semantic encoding: {e}")
            return self._empty_result()

    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'version': '2.0',
            'document': {'version': '2.0', 'text': '', 'sentences': []},
            'text': '',
            'sentence_count': 0,
            'pattern_types': [],
        }

    def _extract_legacy(self, text: str) -> Dict:
        """Legacy spaCy extraction (for rollback)."""
        if not self.nlp:
            return self._empty_result()

        doc = self.nlp(text)

        verb_phrases = []
        noun_phrases = []
        tokens = []

        # Extract noun chunks
        for chunk in doc.noun_chunks:
            noun_phrases.append({
                'text': chunk.text,
                'root': chunk.root.text,
                'root_lemma': chunk.root.lemma_,
            })

        # Extract verb phrases
        for token in doc:
            tokens.append({
                'text': token.text,
                'pos': token.pos_,
                'lemma': token.lemma_,
            })

            if token.pos_ == "VERB":
                verb_phrases.append({
                    'text': token.text,
                    'root': token.text,
                    'root_lemma': token.lemma_,
                })

        return {
            'version': '1.0',
            'verb_phrases': verb_phrases,
            'noun_phrases': noun_phrases,
            'tokens': tokens,
            'stats': {
                'verb_phrase_count': len(verb_phrases),
                'noun_phrase_count': len(noun_phrases),
            }
        }

    def is_available(self) -> bool:
        """Check if semantic service is available."""
        if self.legacy_mode:
            return self.model_loaded and self.nlp is not None
        return True  # semantic-bit has no external dependencies

    def create_highlighted_html(self, text: str) -> str:
        """
        Create HTML with color-coded semantic patterns.

        v2.0: Highlights Points (nouns) and Lines (verbs/predicates)
        v1.0: Legacy verb/noun highlighting
        """
        if not text:
            return ""

        if self.legacy_mode:
            return self._create_highlighted_html_legacy(text)

        try:
            result = semantic_bit.encode_text_to_sb(text)

            # Simple implementation: highlight by sentence patterns
            html_parts = []

            for sentence in result.get('sentences', []):
                sentence_type = sentence.get('type')

                if sentence_type == 'triple':
                    # Point-Line-Point pattern
                    subject = sentence.get('subject', {}).get('text', '')
                    predicate = sentence.get('predicate', {}).get('text', '')
                    obj = sentence.get('object', {}).get('text', '')

                    html_parts.append(format_html(
                        '<span class="semantic-point" style="color: #10B981 !important; font-weight: 500 !important;" '
                        'title="Point (Subject)">{}</span> ',
                        subject
                    ))
                    html_parts.append(format_html(
                        '<span class="semantic-line" style="color: #3B82F6 !important; font-weight: 500 !important;" '
                        'title="Line (Predicate)">{}</span> ',
                        predicate
                    ))
                    html_parts.append(format_html(
                        '<span class="semantic-point" style="color: #10B981 !important; font-weight: 500 !important;" '
                        'title="Point (Object)">{}</span> ',
                        obj
                    ))

                elif sentence_type == 'pointpoint':
                    # Two points connected
                    first = sentence.get('first', {}).get('text', '')
                    second = sentence.get('second', {}).get('text', '')

                    html_parts.append(format_html(
                        '<span class="semantic-point" style="color: #10B981 !important; font-weight: 500 !important;">{}</span> ',
                        first
                    ))
                    html_parts.append(format_html(
                        '<span class="semantic-point" style="color: #10B981 !important; font-weight: 500 !important;">{}</span> ',
                        second
                    ))

                else:
                    # Fallback: render raw text
                    raw_text = sentence.get('text', '')
                    html_parts.append(format_html('<span>{}</span> ', raw_text))

            return mark_safe(''.join(html_parts))

        except Exception as e:
            print(f"Error creating highlighted HTML: {e}")
            return mark_safe(f'<span>{text}</span>')

    def _create_highlighted_html_legacy(self, text: str) -> str:
        """Legacy spaCy-based highlighting."""
        if not self.nlp:
            return text

        doc = self.nlp(text)
        html_parts = []

        for token in doc:
            if token.text.isspace():
                html_parts.append(token.text)
                continue

            if token.pos_ == "VERB":
                html_parts.append(format_html(
                    '<span style="color: #3B82F6 !important; font-weight: 500 !important;">{}</span>',
                    token.text
                ))
            elif token.pos_ == "NOUN":
                html_parts.append(format_html(
                    '<span style="color: #10B981 !important; font-weight: 500 !important;">{}</span>',
                    token.text
                ))
            else:
                html_parts.append(token.text)

            if token.whitespace_:
                html_parts.append(token.whitespace_)

        return mark_safe(''.join(html_parts))

    def get_semantic_relationships(self, text: str) -> List[Tuple]:
        """
        Extract semantic relationships (triples).

        v2.0: Returns Point-Line-Point triples
        v1.0: Returns subject-verb-object (legacy)
        """
        if not text:
            return []

        if self.legacy_mode:
            return self._get_relationships_legacy(text)

        try:
            result = semantic_bit.encode_text_to_sb(text)
            relationships = []

            for sentence in result.get('sentences', []):
                if sentence.get('type') == 'triple':
                    relationships.append({
                        'subject': sentence.get('subject', {}).get('text'),
                        'predicate': sentence.get('predicate', {}).get('text'),
                        'object': sentence.get('object', {}).get('text'),
                    })

            return relationships
        except Exception as e:
            print(f"Error extracting relationships: {e}")
            return []

    def _get_relationships_legacy(self, text: str) -> List[Tuple]:
        """Legacy spaCy relationship extraction."""
        if not self.nlp:
            return []

        doc = self.nlp(text)
        relationships = []

        for token in doc:
            if token.pos_ == "VERB":
                subject = None
                obj = None

                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        subject = child.text
                    elif child.dep_ in ["dobj", "pobj"]:
                        obj = child.text

                if subject or obj:
                    relationships.append({
                        'verb': token.text,
                        'subject': subject,
                        'object': obj
                    })

        return relationships


# Singleton instance
semantic_service = SemanticService()
```

**Key Features**:
- ✅ Feature flag support (`FEATURE_SEMANTIC_V2`)
- ✅ Backward compatibility (legacy spaCy mode)
- ✅ Same interface as before
- ✅ Graceful error handling
- ✅ JSON-serializable output

---

## Step 5: Update semantic_service.py - Things App (45 minutes)

### 5.1 Backup and Copy

```bash
# Backup
cp apps/things/services/semantic_service.py apps/things/services/semantic_service.py.bak

# Copy from dreams (they're nearly identical)
cp apps/dreams/services/semantic_service.py apps/things/services/semantic_service.py
```

**Note**: Both apps have identical semantic service implementations, so we can reuse the code.

---

## Step 6: Update Views - Dreams App (30 minutes)

### 6.1 Update Import (No Change Needed)

**File**: `/home/jblac/projects/newdreamflow/apps/dreams/views.py`

Line 14 already imports:
```python
from .services.semantic_service import semantic_service
```

No change needed - interface is the same!

### 6.2 Update Storage Pattern

**Current Pattern** (appears 3 times in views.py):
```python
semantic_analysis = semantic_service.extract_semantic_bits(content)
dream.semantic_verbs = semantic_analysis.get('verbs', [])
dream.semantic_nouns = semantic_analysis.get('nouns', [])
dream.semantic_bits = semantic_analysis
```

**New Pattern**:
```python
semantic_analysis = semantic_service.extract_semantic_bits(content)
# Store full document in semantic_bits field
dream.semantic_bits = semantic_analysis
# Deprecated fields (keep empty for now, can remove in future)
dream.semantic_verbs = []
dream.semantic_nouns = []
```

**Locations to Update**:

1. **Line 55-58** (`quick_capture` view - auto-save):
```python
# OLD:
if content:
    semantic_analysis = semantic_service.extract_semantic_bits(content)
    dream.semantic_verbs = semantic_analysis.get('verbs', [])
    dream.semantic_nouns = semantic_analysis.get('nouns', [])
    dream.semantic_bits = semantic_analysis

# NEW:
if content:
    semantic_analysis = semantic_service.extract_semantic_bits(content)
    dream.semantic_bits = semantic_analysis
    dream.semantic_verbs = []  # Deprecated
    dream.semantic_nouns = []  # Deprecated
```

2. **Line 82-86** (`quick_capture` view - new dream):
```python
# Same change as above
```

3. **Line 121-124** (`quick_capture` view - form submission):
```python
# Same change as above
```

4. **Line 255-258** (`dream_create` view):
```python
# Same change as above
```

5. **Line 310-313** (`dream_edit` view):
```python
# Same change as above
```

**Total Changes**: 5 locations in dreams/views.py

---

## Step 7: Update Views - Things App (30 minutes)

### 7.1 Same Changes

**File**: `/home/jblac/projects/newdreamflow/apps/things/views.py`

Apply identical changes to `things` app views (same pattern, different model name).

**Search for**: `semantic_analysis = semantic_service.extract_semantic_bits`

**Replace pattern**: Same as dreams app (Step 6.2)

---

## Step 8: Test the Migration (30 minutes)

### 8.1 Run Django Server

```bash
cd ~/projects/newdreamflow
source .venv/bin/activate
python manage.py runserver 0.0.0.0:3000
```

### 8.2 Manual Test: Create Dream

1. Navigate to http://localhost:3000
2. Log in
3. Create new dream with text: "I was flying over the ocean with dolphins"
4. Save

### 8.3 Check Database

```bash
python manage.py shell
```

```python
from apps.dreams.models import Dream

# Get latest dream
dream = Dream.objects.latest('created_at')

print("Version:", dream.semantic_bits.get('version'))
# Expected: "2.0"

print("Sentences:", len(dream.semantic_bits['document']['sentences']))
# Expected: 1+

print("Pattern types:", dream.semantic_bits.get('pattern_types'))
# Expected: ['triple'] or similar

# Check deprecated fields are empty
print("Verbs (deprecated):", dream.semantic_verbs)
# Expected: []

print("Nouns (deprecated):", dream.semantic_nouns)
# Expected: []
```

### 8.4 Test Feature Flag Rollback

**Disable v2.0**:
```bash
# Edit .env
FEATURE_SEMANTIC_V2=false
```

**Restart server and create new dream**:
```bash
python manage.py runserver 0.0.0.0:3000
```

**Check it uses legacy mode**:
```python
dream = Dream.objects.latest('created_at')
print("Version:", dream.semantic_bits.get('version'))
# Expected: "1.0"

print("Verb phrases:", len(dream.semantic_bits.get('verb_phrases', [])))
# Expected: 1+
```

**Re-enable v2.0**:
```bash
# Edit .env
FEATURE_SEMANTIC_V2=true
```

---

## Step 9: Data Migration Script (Optional, 1 hour)

### 9.1 Create Management Command

**File**: `/home/jblac/projects/newdreamflow/apps/dreams/management/commands/migrate_semantic_v2.py`

```python
"""
Django management command to re-encode existing dreams with semantic-bit v2.0
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.dreams.models import Dream
from apps.dreams.services.semantic_service import semantic_service
from apps.things.models import Thing
from apps.things.services.semantic_service import semantic_service as thing_semantic_service


class Command(BaseCommand):
    help = 'Migrate existing dreams/things to semantic-bit v2.0 format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually migrating',
        )
        parser.add_argument(
            '--model',
            type=str,
            default='both',
            choices=['dreams', 'things', 'both'],
            help='Which model to migrate (default: both)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of records to migrate',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        model_choice = options['model']
        limit = options['limit']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        # Migrate dreams
        if model_choice in ['dreams', 'both']:
            self.migrate_dreams(dry_run, limit)

        # Migrate things
        if model_choice in ['things', 'both']:
            self.migrate_things(dry_run, limit)

        self.stdout.write(self.style.SUCCESS('Migration complete!'))

    def migrate_dreams(self, dry_run, limit):
        # Find dreams with old format (version 1.0 or missing version)
        dreams = Dream.objects.filter(
            Q(semantic_bits__version='1.0') |
            Q(semantic_bits__version__isnull=True) |
            ~Q(semantic_bits__has_key='version')
        ).exclude(description='')

        if limit:
            dreams = dreams[:limit]

        total = dreams.count()
        self.stdout.write(f'Found {total} dreams to migrate')

        for i, dream in enumerate(dreams, 1):
            self.stdout.write(f'[{i}/{total}] Migrating dream {dream.pk}')

            if not dry_run:
                try:
                    semantic_analysis = semantic_service.extract_semantic_bits(dream.description)
                    dream.semantic_bits = semantic_analysis
                    dream.semantic_verbs = []
                    dream.semantic_nouns = []
                    dream.save(update_fields=['semantic_bits', 'semantic_verbs', 'semantic_nouns'])
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))

    def migrate_things(self, dry_run, limit):
        # Same logic for things
        things = Thing.objects.filter(
            Q(semantic_bits__version='1.0') |
            Q(semantic_bits__version__isnull=True) |
            ~Q(semantic_bits__has_key='version')
        ).exclude(description='')

        if limit:
            things = things[:limit]

        total = things.count()
        self.stdout.write(f'Found {total} things to migrate')

        for i, thing in enumerate(things, 1):
            self.stdout.write(f'[{i}/{total}] Migrating thing {thing.pk}')

            if not dry_run:
                try:
                    semantic_analysis = thing_semantic_service.extract_semantic_bits(thing.description)
                    thing.semantic_bits = semantic_analysis
                    thing.semantic_verbs = []
                    thing.semantic_nouns = []
                    thing.save(update_fields=['semantic_bits', 'semantic_verbs', 'semantic_nouns'])
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
```

### 9.2 Run Migration

```bash
# Dry run first
python manage.py migrate_semantic_v2 --dry-run

# Migrate dreams only
python manage.py migrate_semantic_v2 --model dreams

# Migrate things only
python manage.py migrate_semantic_v2 --model things

# Migrate both with limit
python manage.py migrate_semantic_v2 --limit 10
```

---

## Step 10: Template Updates (Optional, 1-2 hours)

### 10.1 Assess Template Changes

**Files to check**:
```
templates/dreams/partials/*.html
templates/things/partials/*.html
```

**Look for**:
- Hardcoded references to `semantic_verbs` or `semantic_nouns`
- Color coding logic
- JavaScript that parses semantic data

### 10.2 Update Color Scheme (If Needed)

**Current**: Verbs (blue) / Nouns (green)
**New**: Lines (blue) / Points (green)

**No change needed** if templates just render `semantic_html` from service.

---

## Rollback Plan

If something goes wrong:

### Quick Rollback (5 minutes)

1. **Disable v2.0**:
   ```bash
   # Edit .env
   FEATURE_SEMANTIC_V2=false
   ```

2. **Restart server**:
   ```bash
   python manage.py runserver
   ```

3. **Restore backups** (if made changes):
   ```bash
   mv apps/dreams/services/semantic_service.py.bak apps/dreams/services/semantic_service.py
   mv apps/things/services/semantic_service.py.bak apps/things/services/semantic_service.py
   ```

### Full Rollback (30 minutes)

1. **Revert git branch**:
   ```bash
   git checkout main
   git branch -D feature/semantic-bit-v2
   ```

2. **Restore database** (if backed up):
   ```bash
   # Restore from backup
   ```

3. **Verify legacy mode works**:
   - Create test dream
   - Check spaCy format in database

---

## Success Criteria

Phase D is complete when:

- [ ] ✅ semantic_bit v2.0 installed in newdreamflow venv
- [ ] ✅ Feature flag `FEATURE_SEMANTIC_V2` added to settings
- [ ] ✅ `.env` duplicate fixed
- [ ] ✅ `semantic_service.py` updated in dreams app
- [ ] ✅ `semantic_service.py` updated in things app
- [ ] ✅ Views updated (5 locations in dreams, similar in things)
- [ ] ✅ Manual test: Create dream with v2.0 format
- [ ] ✅ Manual test: Feature flag rollback works
- [ ] ✅ Optional: Data migration script created
- [ ] ✅ Optional: Existing data migrated
- [ ] ✅ Code committed to feature branch

---

## Next Steps

After Phase D:

**Phase E**: Test GPU integration with hardened server
**Phase F**: Polish, documentation, and deployment

---

## Estimated Timeline

| Task | Duration | Notes |
|------|----------|-------|
| Environment setup | 15 min | Install/verify semantic_bit |
| Fix .env | 5 min | Remove duplicate |
| Update settings | 10 min | Add feature flag |
| Update dreams semantic_service | 45 min | Core implementation |
| Update things semantic_service | 45 min | Copy from dreams |
| Update dreams views | 30 min | 5 locations |
| Update things views | 30 min | Similar changes |
| Manual testing | 30 min | Create/verify dreams |
| Data migration script | 1 hour | Optional |
| Template updates | 1-2 hours | Optional |
| **Total** | **4-6 hours** | Without optional tasks: ~3.5 hours |

---

## Questions for User

Before proceeding:

1. **Data Migration**: Should we migrate existing dreams immediately or use lazy migration?
2. **Template Updates**: Are there custom templates that need updating?
3. **Testing**: Is there a test suite we should run?
4. **Deployment**: Production or development environment?

---

**End of Migration Plan**
