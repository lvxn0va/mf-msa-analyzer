---
project: 'AI Multifamily Deep Research Engine (GEMINI VARIANT)'
created: '2026-01-18'
last_updated: '2026-01-19'
total_stories: 32
completed: 18
in_progress: 0
pending: 14
variant: 'gemini-research'
---

# User Stories Backlog (GEMINI VARIANT)

This document contains detailed, sprint-ready user stories for the AI Multifamily Deep Research & Decision Engine **using Gemini for deep research**.

**Branch:** `claude/gemini-deep-research-engine`
**Comparison:** Perplexity version at `claude/ai-multifamily-research-engine-bsVW3`

---

## Story Status Legend

- COMPLETE: Implemented and tested
- IN PROGRESS: Currently being developed
- READY: Ready for development
- BLOCKED: Waiting on dependency
- FUTURE: Planned for later phase

---

## Epic 1: Infrastructure & Environment Setup

### Story 1.1: Python Environment Setup
**Status:** COMPLETE

**Story:**
As a developer,
I want a properly configured Python virtual environment,
So that I can run tests and services without dependency conflicts.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 1.1.1 | I am in the project root | I run `./venv-tests/bin/python --version` | Python 3.13.x is displayed |
| 1.1.2 | I am in the project root | I run `./venv-tests/bin/python tests/test_gauntlet.py` | All tests pass without import errors |
| 1.1.3 | I have shell aliases for python | I activate venv | Aliases do not override venv python |

**Technical Notes:**
- Virtual environment: `venv-tests/`
- Shell alias fix in `~/.zshrc` prevents conflicts

---

### Story 1.2: Git Repository Configuration
**Status:** COMPLETE

**Story:**
As a developer,
I want a properly configured git repository,
So that I can track changes and collaborate effectively.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 1.2.1 | I am in the project root | I run `git status` | Working tree is clean |
| 1.2.2 | I am in the project root | I run `git remote -v` | Origin points to GitHub repo |
| 1.2.3 | The project has sensitive files | I check `.gitignore` | venv, .env, credentials are excluded |

---

### Story 1.3: API Credentials Template
**Status:** READY

**Story:**
As a developer,
I want a `.env.example` file documenting required credentials,
So that new team members can configure their environment.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 1.3.1 | I am setting up the project | I view `.env.example` | I see all required API keys listed |
| 1.3.2 | Required keys include | - | GEMINI_API_KEY, GOOGLE_CLOUD_PROJECT (no Perplexity needed) |
| 1.3.3 | The file exists | I copy to `.env` | I can fill in my credentials |

**Tasks:**
- [ ] Create `.env.example` file
- [ ] Document each variable with comments
- [ ] Add `.env` to `.gitignore` (if not already)

---

## Epic 2: Data Schema & Validation Framework

### Story 2.1: MSA Criteria Schema
**Status:** COMPLETE

**Story:**
As the Logic Engine,
I want a JSON schema defining all 16 MSA-level criteria,
So that I know exactly what metrics and thresholds to evaluate.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 2.1.1 | I access `schemas/msa-criteria.json` | I parse the file | Exactly 16 criteria are defined |
| 2.1.2 | Each criterion | I inspect it | Has: id, metric, threshold, category |
| 2.1.3 | IDs follow pattern | I validate | msa_1 through msa_16 |

---

### Story 2.2: Sub-Market Criteria Schema
**Status:** COMPLETE

**Story:**
As the Logic Engine,
I want a JSON schema defining all 14 Sub-Market criteria,
So that I evaluate location-specific metrics correctly.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 2.2.1 | I access `schemas/submarket-criteria.json` | I parse the file | Exactly 14 criteria are defined |
| 2.2.2 | Each criterion | I inspect it | Has: id, metric, threshold, radius |
| 2.2.3 | IDs follow pattern | I validate | sub_1 through sub_14 |

---

### Story 2.3: Heat Map Output Schema
**Status:** COMPLETE

**Story:**
As the PDF Generator,
I want a JSON schema for heat map validation,
So that I reject malformed input before generating PDFs.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 2.3.1 | I access `schemas/heat-map-schema.json` | I review it | Schema enforces 30 items exactly |
| 2.3.2 | Each item | Must have | id, metric, threshold, value, status, reasoning, source |
| 2.3.3 | Status values | Are validated | Only GREEN, YELLOW, RED accepted |
| 2.3.4 | Reasoning field | Is validated | Minimum 20 characters required |

---

## Epic 3: n8n Workflow Orchestration

### Story 3.1: Webhook Trigger Configuration
**Status:** COMPLETE

**Story:**
As the n8n workflow,
I want a webhook endpoint configured,
So that external clients can trigger analysis.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 3.1.1 | n8n is running | I POST to webhook URL | Workflow triggers |
| 3.1.2 | Payload contains | address, deal_name | Values are extracted correctly |
| 3.1.3 | Payload contains | context_files (optional) | Files are passed to parser node |
| 3.1.4 | Payload is invalid | Missing required fields | Error response returned |

**Tasks:**
- [ ] Import `main-workflow.json` into n8n
- [ ] Configure webhook URL
- [ ] Test with sample payloads

---

### Story 3.2: Google Drive Integration
**Status:** READY

**Story:**
As the n8n workflow,
I want to fetch criteria PDFs from Google Drive,
So that the Logic Engine has the "Immutable Laws".

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 3.2.1 | Google Drive OAuth is configured | I trigger the workflow | MSA-Criteria.pdf is fetched |
| 3.2.2 | Same OAuth | I trigger the workflow | Sub-Market-Neighborhood.pdf is fetched |
| 3.2.3 | PDFs are fetched | In parallel | Both complete before research node |
| 3.2.4 | Drive is unreachable | Workflow handles error | Graceful failure with error message |

**Tasks:**
- [ ] Upload criteria PDFs to Google Drive
- [ ] Configure OAuth2 credentials in n8n
- [ ] Set `MSA_CRITERIA_FILE_ID` and `SUBMARKET_CRITERIA_FILE_ID` env vars
- [ ] Test PDF retrieval

---

### Story 3.3: Workflow Error Handling
**Status:** READY

**Story:**
As the n8n workflow,
I want comprehensive error handling,
So that failures are captured and reported.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 3.3.1 | Perplexity API fails | Workflow continues | Affected criteria marked YELLOW |
| 3.3.2 | Gemini API fails | Workflow stops | Error returned to client |
| 3.3.3 | PDF Service fails | Error is captured | Client notified with error details |
| 3.3.4 | Any node fails | Error is logged | Debugging info available |

**Tasks:**
- [ ] Add error handlers to each node
- [ ] Configure fallback behavior for research failures
- [ ] Implement error response formatting

---

## Epic 4: Research Engine (Gemini Deep Research)

### Story 4.1: Research Prompt Template
**Status:** READY (needs Gemini adaptation)

**Story:**
As the Research Engine,
I want a prompt template for Gemini deep research with grounding,
So that Gemini gathers all required data points with citations.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 4.1.1 | I access `prompts/gemini-research-prompt.txt` | I read it | Prompt requests 1-3-5 mile data |
| 4.1.2 | Prompt specifies | Data points | Population, crime, schools, amenities, transport |
| 4.1.3 | Prompt requires | Citations | Source URL and grounding references |
| 4.1.4 | Prompt enables | Grounding | Uses Google Search for real-time data |

**Tasks:**
- [ ] Create `prompts/gemini-research-prompt.txt`
- [ ] Enable grounding configuration in prompt
- [ ] Test with sample addresses

---

### Story 4.2: Gemini Deep Research Integration
**Status:** READY

**Story:**
As the n8n workflow,
I want to call Gemini with Deep Research/Grounding enabled,
So that I gather comprehensive live demographic research with citations.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 4.2.1 | I have GEMINI_API_KEY | I call Gemini with grounding | Research data is returned |
| 4.2.2 | Grounding is enabled | I query for demographics | Real-time data with citations |
| 4.2.3 | Response is received | Data includes | All 30 data points with source URLs |
| 4.2.4 | Research quality | Is compared | Matches or exceeds Background folder samples |

**Implementation Notes:**
- Uses Gemini API with grounding/deep research enabled
- Model: TBD (gemini-2.0-flash with grounding or deep research mode)
- Single API call pattern (vs Perplexity async)
- Must match quality of sample outputs in Background folder

**Tasks:**
- [ ] Research Gemini deep research API options
- [ ] Configure grounding in n8n HTTP Request
- [ ] Test research quality vs Perplexity
- [ ] Create new workflow nodes

---

### Story 4.3: Citation Validation
**Status:** READY

**Story:**
As the Research Engine,
I want to validate all citations are real,
So that no hallucinated sources appear in reports.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 4.3.1 | Research returns citations | Each source | Has URL and grounding reference |
| 4.3.2 | Citation format | Is standardized | Gemini grounding format |
| 4.3.3 | Missing citation | For any data point | Data point flagged for review |

**Tasks:**
- [ ] Parse grounding metadata from Gemini response
- [ ] Validate source URLs
- [ ] Standardize citation format for PDF output

---

## Epic 5: Logic Engine (Gemini Integration)

### Story 5.1: Gemini System Prompt
**Status:** COMPLETE

**Story:**
As the Logic Engine,
I want a system prompt enforcing strict evaluation,
So that all 30 criteria are evaluated consistently.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 5.1.1 | I access `prompts/gemini-system-prompt.txt` | I read it | No hallucination rule is present |
| 5.1.2 | Prompt enforces | Context override hierarchy | Tier 1 > Tier 2 > Tier 3 |
| 5.1.3 | Prompt requires | Exactly 30 items | Output validation specified |
| 5.1.4 | Prompt specifies | Goldilocks logic | For amenities, transport, vacancy |

---

### Story 5.2: Gemini Logic Engine Integration
**Status:** COMPLETE

**Story:**
As the n8n workflow,
I want to call Gemini via HTTP Request,
So that I perform deterministic property analysis.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 5.2.1 | Gemini API key configured | I call Gemini | Response is received |
| 5.2.2 | Temperature setting | Is 0.1 | Deterministic outputs |
| 5.2.3 | Response format | Is JSON | Valid heat map array with 30 items |
| 5.2.4 | Processing time | Is measured | ~30-60 seconds typical |

**Implementation Notes:**
- Uses HTTP Request node with Query Auth credential
- Model: `gemini-2.5-flash` with temperature 0.1
- Response MIME type set to `application/json`
- Validates exactly 30 items with GREEN/YELLOW/RED status

---

### Story 5.3: Goldilocks Logic Validation
**Status:** COMPLETE (tested in Gauntlet)

**Story:**
As the Logic Engine,
I want Goldilocks logic for distance-based criteria,
So that extremes in either direction are flagged.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 5.3.1 | Amenities at 0.2 miles | I evaluate | Status is RED |
| 5.3.2 | Amenities at 1.5 miles | I evaluate | Status is GREEN |
| 5.3.3 | Amenities at 3 miles | I evaluate | Status is YELLOW or RED |
| 5.3.4 | Vacancy at 5% | I evaluate | Status is GREEN |
| 5.3.5 | Vacancy at 2% | I evaluate | Status is YELLOW |
| 5.3.6 | Vacancy at 9% | I evaluate | Status is RED |

---

### Story 5.4: JSON Output Validation
**Status:** COMPLETE (tested in Gauntlet)

**Story:**
As the n8n workflow,
I want to validate Gemini's JSON output,
So that malformed responses are caught before PDF generation.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 5.4.1 | JSON response received | I validate | Exactly 30 items |
| 5.4.2 | Each item | Is validated | All required fields present |
| 5.4.3 | Status values | Are validated | Only GREEN/YELLOW/RED |
| 5.4.4 | Reasoning | Is validated | Minimum 20 characters |
| 5.4.5 | Validation fails | Workflow handles | Error returned, no PDF generated |

---

## Epic 6: Context Override System

### Story 6.1: Document Type Detection
**Status:** READY

**Story:**
As the Context Override System,
I want to identify uploaded document types,
So that I apply correct extraction rules.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 6.1.1 | Document contains "abatement" | I analyze | Type is TAX_ABATEMENT |
| 6.1.2 | Document contains "rent roll" | I analyze | Type is RENT_ROLL |
| 6.1.3 | Document contains "appraisal" | I analyze | Type is APPRAISAL |
| 6.1.4 | Unknown document | I analyze | Type is OTHER |

**Tasks:**
- [ ] Implement keyword-based document classification
- [ ] Handle multiple documents of same type
- [ ] Log document types for debugging

---

### Story 6.2: Tax Abatement Override
**Status:** READY

**Story:**
As the Context Override System,
I want to extract tax abatement details,
So that Taxes/Fees criterion reflects actual property terms.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 6.2.1 | Tax abatement document uploaded | I extract | Abatement percentage found |
| 6.2.2 | Extraction successful | Override applied | sub_13 uses abated rate |
| 6.2.3 | Override applied | In heat map | override_applied = true |
| 6.2.4 | Override applied | In heat map | override_document = filename |

**Tasks:**
- [ ] Parse abatement percentage from document
- [ ] Extract duration (years) if available
- [ ] Map to sub_13 criterion
- [ ] Set override flags in output

---

### Story 6.3: Rent Roll Override
**Status:** READY

**Story:**
As the Context Override System,
I want to extract rent roll data,
So that actual occupancy overrides market vacancy rates.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 6.3.1 | Rent roll document uploaded | I extract | Occupancy rate found |
| 6.3.2 | Property occupancy 98% | Override context provided | Property-level note added |
| 6.3.3 | MSA vacancy remains | In evaluation | MSA-level risk still assessed |

**Tasks:**
- [ ] Parse occupancy from rent roll
- [ ] Add as context note (not full override for MSA)
- [ ] Include in reasoning for msa_8

---

## Epic 7: PDF Generation Service

### Story 7.1: FastAPI Health Endpoint
**Status:** COMPLETE

**Story:**
As a DevOps Engineer,
I want a health check endpoint,
So that I can monitor service availability.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 7.1.1 | PDF service is running | I GET /health | Response is 200 OK |
| 7.1.2 | Service is starting | I GET /health | Response indicates "starting" |
| 7.1.3 | Service is unhealthy | I GET /health | Response is 503 |

---

### Story 7.2: Heat Map PDF Generation
**Status:** COMPLETE

**Story:**
As the n8n workflow,
I want to generate a Heat Map PDF via PDF Noodle API,
So that users see the 30-point grid at a glance.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 7.2.1 | Valid heat map JSON received | I generate PDF | File is created |
| 7.2.2 | PDF content | Includes | Color-coded rows (Green/Yellow/Red) |
| 7.2.3 | PDF content | Includes | Summary statistics |
| 7.2.4 | PDF content | Includes | Recommendation badge |
| 7.2.5 | Invalid JSON received | I reject | Error response with details |

**Implementation Notes:**
- Uses PDF Noodle API (`/v1/html-to-pdf/sync`)
- HTML built dynamically in "Build Heat Map HTML" Code node
- Returns signed URL valid for 24 hours
- Includes color-coded status badges and summary statistics

---

### Story 7.3: Investment Brief PDF Generation
**Status:** READY (future enhancement)

**Story:**
As the PDF Service,
I want to generate an Investment Brief PDF,
So that users get detailed narrative analysis.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 7.3.1 | Valid heat map JSON received | I generate PDF | File is created |
| 7.3.2 | PDF content | Includes | Executive summary |
| 7.3.3 | PDF content | Includes | Section-by-section analysis |
| 7.3.4 | PDF content | Includes | Source citations in footnotes |
| 7.3.5 | PDF content | Includes | Final recommendation with justification |

**Tasks:**
- [ ] Test with sample heat map JSON
- [ ] Verify narrative quality
- [ ] Verify all citations appear
- [ ] Test override indicators

---

### Story 7.4: PDF Auto-Cleanup
**Status:** COMPLETE

**Story:**
As the PDF Service,
I want automatic cleanup of old PDFs,
So that storage doesn't grow unbounded.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 7.4.1 | PDF is older than 24 hours | Cleanup runs | PDF is deleted |
| 7.4.2 | PDF is less than 24 hours old | Cleanup runs | PDF is retained |
| 7.4.3 | Cleanup | Runs automatically | On schedule or startup |

---

## Epic 8: Frontend Integration

### Story 8.1: Property Input Form
**Status:** FUTURE

**Story:**
As an Acquisition Manager,
I want a web form to enter property details,
So that I can start an analysis with minimal effort.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 8.1.1 | I access the application | I see a form | Address and Deal Name fields visible |
| 8.1.2 | I enter an address | Autocomplete suggests | Valid addresses appear |
| 8.1.3 | I submit the form | Required fields empty | Validation errors shown |
| 8.1.4 | I submit valid data | Form submits | Analysis begins |

---

### Story 8.2: File Upload Component
**Status:** FUTURE

**Story:**
As an Acquisition Manager,
I want to upload context documents,
So that my property-specific data is included in analysis.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 8.2.1 | I have a PDF file | I drag to upload area | File is accepted |
| 8.2.2 | File is >10MB | I try to upload | Error: file too large |
| 8.2.3 | File is wrong type | I try to upload | Error: invalid file type |
| 8.2.4 | Upload in progress | I see indicator | Progress percentage shown |

---

### Story 8.3: Results Display
**Status:** FUTURE

**Story:**
As an Acquisition Manager,
I want to see analysis results in the browser,
So that I can quickly review before downloading PDFs.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 8.3.1 | Analysis completes | I see results | Recommendation prominently displayed |
| 8.3.2 | Results page | Shows | Summary of GREEN/YELLOW/RED counts |
| 8.3.3 | Results page | Has | Download buttons for both PDFs |
| 8.3.4 | I click download | PDF downloads | Correct file is received |

---

## Epic 9: Testing & Quality Assurance

### Story 9.1-9.6: Gauntlet Tests
**Status:** COMPLETE (7/7 passing)

All Gauntlet tests are implemented and passing:
- Ghost Town Test
- War Zone Test
- Context Override Test
- Completeness Check
- Goldilocks Amenities Test
- Goldilocks Vacancy Test
- Recommendation Logic Test

---

## Epic 10: Deployment & Operations

### Story 10.1: PDF Service Docker Image
**Status:** READY

**Story:**
As a DevOps Engineer,
I want to containerize the PDF service,
So that deployment is consistent and reproducible.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 10.1.1 | Dockerfile exists | I build image | Build succeeds |
| 10.1.2 | Image is built | I run container | Service starts |
| 10.1.3 | Container running | I call /health | 200 OK returned |
| 10.1.4 | Container running | I call /generate-pdf | PDF is generated |

**Tasks:**
- [ ] Verify Dockerfile in pdf-service/
- [ ] Build and test locally
- [ ] Push to container registry
- [ ] Document deployment steps

---

### Story 10.2: n8n Production Setup
**Status:** READY

**Story:**
As a DevOps Engineer,
I want n8n deployed with production configuration,
So that the workflow runs reliably in production.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 10.2.1 | n8n is deployed | I access UI | Workflow is visible |
| 10.2.2 | Credentials configured | Workflow executes | All API calls succeed |
| 10.2.3 | Production mode | Error occurs | Alerts are sent |
| 10.2.4 | Queue mode | Multiple requests | Requests are queued |

**Tasks:**
- [ ] Deploy n8n (Cloud or Docker)
- [ ] Import main-workflow.json
- [ ] Configure all credentials
- [ ] Enable queue mode for concurrency
- [ ] Set up error notifications

---

### Story 10.3: Cloud Storage Setup
**Status:** READY

**Story:**
As a DevOps Engineer,
I want cloud storage for generated PDFs,
So that files are accessible and automatically cleaned up.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 10.3.1 | GCS bucket created | PDF is uploaded | File is accessible |
| 10.3.2 | Lifecycle policy set | PDF is >24 hours old | File is deleted |
| 10.3.3 | Signed URL generated | User clicks link | PDF downloads |
| 10.3.4 | Bucket permissions | Are restricted | Only service can write |

**Tasks:**
- [ ] Create GCS bucket
- [ ] Configure lifecycle policy (24-hour retention)
- [ ] Set up service account with write permissions
- [ ] Implement signed URL generation

---

### Story 10.4: Monitoring Dashboard
**Status:** FUTURE

**Story:**
As a DevOps Engineer,
I want a monitoring dashboard,
So that I can track system health and performance.

**Acceptance Criteria:**

| AC | Given | When | Then |
|----|-------|------|------|
| 10.4.1 | Dashboard exists | I access it | Key metrics visible |
| 10.4.2 | Metrics include | Response times | Per-node latency |
| 10.4.3 | Metrics include | Error rates | By node and type |
| 10.4.4 | Alerts configured | Error rate spikes | Notification sent |

---

## Sprint Planning Summary (GEMINI VARIANT)

### Sprint 1: Gemini Research Integration ← CURRENT
- ✅ Story 3.1: Webhook Trigger Configuration
- ⬜ Story 4.1: Research Prompt Template (Gemini adaptation)
- ⬜ Story 4.2: Gemini Deep Research Integration
- ✅ Story 5.2: Gemini Logic Engine Integration
- ✅ Story 7.2: Heat Map PDF Generation (PDF Noodle)

### Sprint 2: Context Overrides & Enhancement
- Story 6.1: Document Type Detection
- Story 6.2: Tax Abatement Override
- Story 6.3: Rent Roll Override
- Story 3.3: Workflow Error Handling
- Story 7.3: Investment Brief PDF Generation

### Sprint 3: Production Readiness
- Story 10.1: PDF Service Docker Image (if self-hosting)
- Story 10.2: n8n Production Setup
- Story 10.3: Cloud Storage Setup
- Story 1.3: API Credentials Template

### Future Sprints: Frontend
- Story 8.1: Property Input Form
- Story 8.2: File Upload Component
- Story 8.3: Results Display
- Story 10.4: Monitoring Dashboard

---

## Current System Status (GEMINI VARIANT)

**Branch:** `claude/gemini-deep-research-engine`
**Status:** Research integration pending

**Architecture:**
1. Webhook receives address + deal_name
2. **Gemini Deep Research** (grounding) gathers all 30 data points ← NEW
3. Gemini evaluates and generates 30-point heat map
4. PDF Noodle generates color-coded Heat Map PDF
5. Response returns JSON with analysis + PDF URL

**Next Steps:**
1. Research Gemini deep research/grounding API options
2. Create new workflow with Gemini research nodes
3. Test and compare output quality vs Perplexity version

**Comparison Branch:** `claude/ai-multifamily-research-engine-bsVW3` (Perplexity - working)

---

_Document updated: 2026-01-19_
_Variant: Gemini Deep Research_
_Total stories: 32 | Complete: 18 | Ready: 14_
