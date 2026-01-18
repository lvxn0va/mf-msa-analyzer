---
project_name: 'AI Multifamily Deep Research & Decision Engine'
user_name: 'shihaya'
date: '2026-01-18'
sections_completed: ['technology_stack', 'implementation_rules', 'architecture', 'testing', 'business_logic']
existing_patterns_found: 12
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| Runtime | Python | 3.13 |
| Orchestrator | n8n | Self-hosted or Cloud |
| Logic Engine | Google Gemini 3 Pro | Via Vertex AI, temperature=0.1 |
| Research Engine | Perplexity Sonar-Pro | Via HTTP Request |
| PDF Service | FastAPI + ReportLab | Port 8000 |
| Frontend | Lovable.dev (React) | Future |
| Storage | Google Drive / GCS | For PDFs |
| Testing | pytest | venv-tests/ |

### Environment Setup
```bash
# Run tests using direct path (avoids shell alias issues)
./venv-tests/bin/python tests/test_gauntlet.py

# PDF service (when ready)
cd pdf-service && source venv/bin/activate && uvicorn app.main:app --reload
```

---

## Critical Implementation Rules

### 1. The 30-Point Framework is IMMUTABLE
- **NEVER** skip, combine, or summarize any of the 30 criteria
- MSA criteria: `msa_1` through `msa_16` (16 points)
- Sub-Market criteria: `sub_1` through `sub_14` (14 points)
- Every criterion MUST have: `id`, `metric`, `threshold`, `value`, `status`, `reasoning` (min 20 chars), `source`

### 2. Status Values are STRICT
```
GREEN  = Meets or exceeds threshold
YELLOW = Marginal, requires human review
RED    = Fails threshold, deal-killer unless exceptional circumstances
```
**NO OTHER VALUES ALLOWED** - no "ORANGE", no "PASS/FAIL", no lowercase

### 3. Context Override Hierarchy (Priority Order)
```
Tier 1 (HIGHEST): User-uploaded documents (tax abatement, rent rolls, appraisals)
Tier 2: Live research data (Perplexity results)
Tier 3 (LOWEST): General market data (Census, CoStar)
```
When override applied, set `override_applied: true` and `override_document: "<filename>"`

### 4. Goldilocks Logic (Critical for 4 Criteria)
These criteria have a "sweet spot" - extremes in EITHER direction are bad:

| Criterion | Too Close | Just Right (GREEN) | Too Far |
|-----------|-----------|-------------------|---------|
| Amenities | <0.25 mi = RED | 1-2 mi = GREEN | >2 mi = YELLOW/RED |
| Transport Access | <0.5 mi = RED (noise) | 1-2 mi = GREEN | >3 mi = YELLOW |
| Vacancy Rate | <3% = YELLOW (overheated) | 4-6% = GREEN | >7% = RED |
| Renter Density | Context-dependent | See below | Context-dependent |

### 5. Context-Aware Evaluation (Urban vs Suburban)
```
URBAN CORE (Downtown, CBD):
  - High renter density >70% = GREEN (expected)
  - Transport proximity <0.5 mi = YELLOW (tolerated)
  - Lower school ratings = YELLOW (families less common)

SUBURBAN (Periphery, Exurbs):
  - Renter density >70% = YELLOW (signals economic distress)
  - Transport proximity <0.5 mi = RED (quality of life concern)
  - School ratings critical = RED if below threshold
```

### 6. Recommendation Thresholds
```python
red_count = sum(1 for item in heat_map if item['status'] == 'RED')

if red_count > 5:
    recommendation = "NO-GO"      # Reject deal
elif red_count >= 3:
    recommendation = "CAUTION"    # Investment Committee review
else:
    recommendation = "PROCEED"    # Full due diligence
```

---

## Architecture Patterns

### Data Flow (Happy Path)
```
User Input → n8n Webhook → Load Criteria PDFs → Parse Context Docs
    → Perplexity Research → Gemini Logic Engine → Validate JSON
    → PDF Service → Return PDF URLs
```

### JSON Schema Validation
The heat map JSON MUST:
1. Be a list/array (not object)
2. Contain exactly 30 items
3. Each item must have all required fields
4. Status must be GREEN, YELLOW, or RED only
5. Reasoning must be minimum 20 characters

### Error Handling
- If Perplexity fails: Mark affected criteria as YELLOW with "Data unavailable" reasoning
- If user document parsing fails: Log error, continue without override
- If JSON validation fails: Return error, do not generate PDFs

---

## Testing Requirements

### The Gauntlet (7 Tests - All Must Pass)
1. **Ghost Town Test**: Population <10k → RED on msa_1
2. **War Zone Test**: Crime > MSA average → RED on sub_1
3. **Context Override Test**: Tax abatement doc → GREEN on sub_12 with override flag
4. **Completeness Check**: Exactly 30 items in heat map
5. **Goldilocks Amenities**: Distance-based status (too close/just right/too far)
6. **Goldilocks Vacancy**: 4-6% = GREEN, extremes = YELLOW/RED
7. **Recommendation Logic**: >5 RED = NO-GO, 3-5 = CAUTION, ≤2 = PROCEED

### Running Tests
```bash
# Always use this command (avoids Python alias issues)
./venv-tests/bin/python tests/test_gauntlet.py
```

---

## File Organization

```
/schemas/           # Source of truth for criteria definitions
  msa-criteria.json
  submarket-criteria.json
  heat-map-schema.json

/prompts/           # AI system prompts (do not modify without review)
  gemini-system-prompt.txt
  perplexity-research-prompt.txt
  context-override-logic.txt

/n8n/workflows/     # Workflow definitions
  main-workflow.json

/pdf-service/       # FastAPI service
  app/main.py
  app/models.py
  app/generators/

/tests/             # Gauntlet test suite
  test_gauntlet.py
```

---

## Code Style Guidelines

### Python
- Use type hints for all function parameters and returns
- Pydantic models for all data validation
- FastAPI for REST endpoints
- Minimum 20-character reasoning for all criteria evaluations

### JSON
- Use snake_case for all keys
- IDs follow pattern: `msa_N` or `sub_N`
- Status values are UPPERCASE

### Prompts
- Never modify system prompts without running full Gauntlet tests
- Temperature = 0.1 for deterministic outputs
- Always include citation requirements in prompts

---

## API Contracts

### PDF Service Endpoint
```
POST /generate-pdf
Content-Type: application/json

{
  "heat_map": [...],      // Exactly 30 items
  "deal_name": "string",  // Max 200 chars
  "address": "string",    // Max 500 chars
  "research_data": {}     // Optional appendix data
}

Response:
{
  "status": "success",
  "analysis_id": "uuid",
  "heat_map_url": "url",
  "investment_brief_url": "url",
  "generated_at": "iso-datetime"
}
```

---

## Common Pitfalls to Avoid

1. **DO NOT** use Python's `python` command directly - use `./venv-tests/bin/python`
2. **DO NOT** change status values to anything other than GREEN/YELLOW/RED
3. **DO NOT** skip criteria or combine them in output
4. **DO NOT** forget override flags when user documents take precedence
5. **DO NOT** ignore Goldilocks logic for amenities/transport/vacancy
6. **DO NOT** use temperature > 0.1 for Gemini (causes inconsistent results)

---

## Quick Reference: The 30 Criteria IDs

### MSA Level (16)
| ID | Metric |
|----|--------|
| msa_1 | Population Size |
| msa_2 | Population Growth |
| msa_3 | In-Migration |
| msa_4 | Employment Growth |
| msa_5 | Income Growth |
| msa_6 | Job Diversity |
| msa_7 | Unemployment Rate |
| msa_8 | Apartment Vacancy Rate |
| msa_9 | Homeowner Vacancy |
| msa_10 | Multifamily Permits |
| msa_11 | Absorption Rate |
| msa_12 | Environmental Risk |
| msa_13 | Cap Rate Spread |
| msa_14 | Landlord-Friendly Laws |
| msa_15 | Affordability Index |
| msa_16 | Proximity to Tier 1 MSA |

### Sub-Market Level (14)
| ID | Metric |
|----|--------|
| sub_1 | Crime Rate |
| sub_2 | School Ratings |
| sub_3 | Transport Avoidance |
| sub_4 | Goldilocks Amenities |
| sub_5 | Proximity to Quality Schools |
| sub_6 | Transport Access |
| sub_7 | Path of Growth |
| sub_8 | Zoning Protections |
| sub_9 | Renter Density |
| sub_10 | Government Volatility |
| sub_11 | Cluster Growth Potential |
| sub_12 | Proximity to MF Assets |
| sub_13 | Taxes/Fees |
| sub_14 | Historical Appreciation |

---

_Last updated: 2026-01-18 | Generated for BMAD agent alignment_
