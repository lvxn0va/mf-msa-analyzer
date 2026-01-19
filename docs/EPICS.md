---
stepsCompleted: ['requirements_extraction', 'epic_design', 'story_outline']
inputDocuments: ['docs/PRD.md', 'docs/ARCHITECTURE.md', 'project-context.md']
created: '2026-01-18'
status: 'Ready for Implementation'
---

# AI Multifamily Deep Research Engine - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for the AI Multifamily Deep Research & Decision Engine, decomposing the requirements from the PRD and Architecture into implementable stories.

---

## Requirements Inventory

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Accept property address and deal name input | P0 |
| FR-02 | Accept context document uploads (PDF, TXT) | P0 |
| FR-03 | Identify MSA (Macro) context from address | P0 |
| FR-04 | Identify Sub-Market (Micro) context from address | P0 |
| FR-05 | Perform live 1-3-5 mile demographic research | P0 |
| FR-06 | Evaluate all 30 criteria points | P0 |
| FR-07 | Apply Goldilocks logic for distance-based criteria | P0 |
| FR-08 | Apply context override from user documents | P0 |
| FR-09 | Generate Decision Heat Map PDF | P0 |
| FR-10 | Generate Investment Brief PDF | P0 |
| FR-11 | Return download URLs to user | P0 |
| FR-12 | Validate JSON output (30 items, valid statuses) | P0 |
| FR-13 | Apply dynamic thresholds (Urban vs Suburban) | P1 |
| FR-14 | Provide source citations for all data | P0 |
| FR-15 | Calculate recommendation (NO-GO/CAUTION/PROCEED) | P0 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Analysis completion time | ~8-9 minutes (deep research) |
| NFR-02 | PDF generation time | <30 seconds |
| NFR-03 | System uptime | 99.5% |
| NFR-04 | Daily throughput (MVP) | 100+ analyses |
| NFR-05 | Data freshness | <6 months |
| NFR-06 | Citation accuracy | 100% real sources |
| NFR-07 | Encryption | At rest and in transit |
| NFR-08 | Data retention | 30 days max |

### Additional Requirements

| ID | Requirement | Type |
|----|-------------|------|
| AR-01 | No user accounts (MVP) | Constraint |
| AR-02 | No financial underwriting | Constraint |
| AR-03 | Mobile-responsive interface | UX |
| AR-04 | WCAG 2.1 Level AA | Accessibility |

---

### FR Coverage Map

| Epic | FR Coverage |
|------|-------------|
| Epic 1: Infrastructure | - |
| Epic 2: Data Schemas | FR-06, FR-12 |
| Epic 3: n8n Workflow | FR-01, FR-02, FR-03, FR-04, FR-11 |
| Epic 4: Research Engine | FR-05, FR-14 |
| Epic 5: Logic Engine | FR-06, FR-07, FR-13, FR-15 |
| Epic 6: Context Override | FR-08 |
| Epic 7: PDF Generation | FR-09, FR-10 |
| Epic 8: Frontend | FR-01, FR-02, FR-11 |
| Epic 9: Testing | FR-12 |
| Epic 10: Deployment | NFR-01 through NFR-08 |

---

## Epic List

1. **Epic 1: Infrastructure & Environment Setup**
2. **Epic 2: Data Schema & Validation Framework**
3. **Epic 3: n8n Workflow Orchestration**
4. **Epic 4: Research Engine (Perplexity Integration)**
5. **Epic 5: Logic Engine (Gemini Integration)**
6. **Epic 6: Context Override System**
7. **Epic 7: PDF Generation Service**
8. **Epic 8: Frontend Integration**
9. **Epic 9: Testing & Quality Assurance**
10. **Epic 10: Deployment & Operations**

---

## Epic 1: Infrastructure & Environment Setup

**Goal:** Establish the foundational infrastructure, development environments, and credential management required for all other epics.

**Status:** COMPLETE (as per handoff note)

### Story 1.1: Python Environment Setup

As a developer,
I want a properly configured Python virtual environment,
So that I can run tests and services without dependency conflicts.

**Acceptance Criteria:**

**Given** I am in the project root directory
**When** I run `./venv-tests/bin/python tests/test_gauntlet.py`
**Then** all tests execute without import errors
**And** the virtual environment is isolated from system Python

### Story 1.2: Git Repository Configuration

As a developer,
I want a properly configured git repository,
So that I can track changes and collaborate effectively.

**Acceptance Criteria:**

**Given** the project is initialized
**When** I run `git status`
**Then** I see a clean working tree
**And** the branch is tracked on origin

### Story 1.3: API Credentials Configuration

As a developer,
I want environment variables configured for all APIs,
So that services can authenticate with external providers.

**Acceptance Criteria:**

**Given** the shell configuration is loaded
**When** I check for `GEMINI_API_KEY`
**Then** the variable is set and accessible
**And** Perplexity, Google Cloud credentials are documented in .env.example

---

## Epic 2: Data Schema & Validation Framework

**Goal:** Define and enforce the 30-point criteria schema that serves as the source of truth for all evaluations.

**Status:** COMPLETE (schemas exist in /schemas)

### Story 2.1: MSA Criteria Schema Definition

As a Logic Engine,
I want a JSON schema defining all 16 MSA-level criteria,
So that I know exactly what metrics and thresholds to evaluate.

**Acceptance Criteria:**

**Given** I access `schemas/msa-criteria.json`
**When** I parse the schema
**Then** I find exactly 16 criteria definitions
**And** each has: id, metric, threshold, category, goldilocks_logic flag

### Story 2.2: Sub-Market Criteria Schema Definition

As a Logic Engine,
I want a JSON schema defining all 14 Sub-Market criteria,
So that I know exactly what location-specific metrics to evaluate.

**Acceptance Criteria:**

**Given** I access `schemas/submarket-criteria.json`
**When** I parse the schema
**Then** I find exactly 14 criteria definitions
**And** each has: id, metric, threshold, radius, evaluation_type

### Story 2.3: Heat Map Output Schema

As a PDF Generator,
I want a JSON schema defining the heat map output format,
So that I can validate all inputs before generating PDFs.

**Acceptance Criteria:**

**Given** I receive heat map JSON from the Logic Engine
**When** I validate against `schemas/heat-map-schema.json`
**Then** it must contain exactly 30 items
**And** each item has: id, metric, threshold, value, status (GREEN|YELLOW|RED), reasoning (min 20 chars), source
**And** override fields are optional but valid when present

---

## Epic 3: n8n Workflow Orchestration

**Goal:** Build the visual workflow that orchestrates all components from input to output.

**Status:** COMPLETE (workflow exists in /n8n/workflows)

### Story 3.1: Webhook Trigger Node

As the n8n workflow,
I want a webhook endpoint that receives property requests,
So that I can initiate the analysis pipeline.

**Acceptance Criteria:**

**Given** a client sends a POST request to the webhook
**When** the payload contains `address`, `deal_name`, and optional `context_files`
**Then** the workflow triggers successfully
**And** input data is extracted for downstream nodes

### Story 3.2: Criteria PDF Loader Node

As the n8n workflow,
I want to load "Immutable Laws" PDFs from storage,
So that the Logic Engine has the criteria definitions.

**Acceptance Criteria:**

**Given** the workflow receives a trigger
**When** I fetch MSA-Criteria.pdf and Sub-Market-Neighborhood.pdf
**Then** both PDFs are retrieved from Google Drive
**And** text is extracted for the context variable

### Story 3.3: User Document Parser Node

As the n8n workflow,
I want to parse user-uploaded context documents,
So that override facts can be extracted for the Logic Engine.

**Acceptance Criteria:**

**Given** the user uploaded context files (PDF/TXT)
**When** I parse the documents
**Then** text content is extracted
**And** document names are preserved for citation

### Story 3.4: Workflow Response Node

As the n8n workflow,
I want to return results to the calling client,
So that the user can download their analysis.

**Acceptance Criteria:**

**Given** PDF generation is complete
**When** I construct the response
**Then** it includes heat_map_url and investment_brief_url
**And** status indicates success or failure with error details

---

## Epic 4: Research Engine (Perplexity Integration)

**Goal:** Implement live demographic research using Perplexity Deep Research API.

**Status:** COMPLETE (async deep research with sonar-deep-research model)

### Story 4.1: Research Prompt Construction

As the Research Engine,
I want a system prompt that guides demographic research,
So that I gather all required data with citations.

**Acceptance Criteria:**

**Given** I have the property address
**When** I construct the research prompt
**Then** it requests 1-mile, 3-mile, and 5-mile radius data
**And** it specifies exact data points: population, crime, schools, amenities, transport

### Story 4.2: Perplexity API Integration

As the n8n workflow,
I want to call Perplexity Sonar-Pro API,
So that I can perform live web research with citations.

**Acceptance Criteria:**

**Given** I have the constructed research prompt
**When** I call the Perplexity API via HTTP Request
**Then** I receive structured research data
**And** each data point includes source URL and date

### Story 4.3: Research Data Normalization

As the Research Engine,
I want to normalize research results to a standard format,
So that the Logic Engine receives consistent input.

**Acceptance Criteria:**

**Given** I receive raw Perplexity response
**When** I normalize the data
**Then** output has `msa_data` and `submarket_data` sections
**And** each metric is mapped to its corresponding criterion ID

---

## Epic 5: Logic Engine (Gemini Integration)

**Goal:** Implement the AI-powered evaluation engine that applies the 30-point criteria.

**Status:** COMPLETE (gemini-2.5-flash via HTTP Request with temperature 0.1)

### Story 5.1: Gemini System Prompt Configuration

As the Logic Engine,
I want a system prompt that enforces strict evaluation rules,
So that I never skip criteria or hallucinate data.

**Acceptance Criteria:**

**Given** I have the Gemini system prompt
**When** I review its instructions
**Then** it enforces: no hallucinations, context override hierarchy, Goldilocks logic
**And** it requires exactly 30 JSON objects with all required fields

### Story 5.2: Vertex AI Integration

As the n8n workflow,
I want to call Google Vertex AI with Gemini,
So that I can perform deterministic analysis.

**Acceptance Criteria:**

**Given** I have research data and criteria context
**When** I call Gemini via Vertex AI node
**Then** temperature is set to 0.1 for consistency
**And** response is valid JSON array

### Story 5.3: Goldilocks Logic Implementation

As the Logic Engine,
I want to apply Goldilocks logic for distance-based criteria,
So that "too close" and "too far" are both correctly flagged.

**Acceptance Criteria:**

**Given** I evaluate Amenities proximity
**When** distance is <0.25 miles
**Then** status is RED (noise, traffic concerns)
**And** when distance is 1-2 miles, status is GREEN
**And** when distance is >2 miles, status is YELLOW or RED

### Story 5.4: Dynamic Threshold Application

As the Logic Engine,
I want to detect location type and apply appropriate thresholds,
So that Urban and Suburban properties are evaluated correctly.

**Acceptance Criteria:**

**Given** I analyze a Downtown property
**When** renter density is >70%
**Then** status is GREEN (expected for urban)
**And** given a Suburban property with >70% renter density
**Then** status is YELLOW (signals distress)

### Story 5.5: Recommendation Calculation

As the Logic Engine,
I want to calculate the final recommendation based on RED count,
So that users get clear GO/NO-GO guidance.

**Acceptance Criteria:**

**Given** the heat map is complete
**When** RED count is >5
**Then** recommendation is "NO-GO"
**And** when RED count is 3-5, recommendation is "CAUTION"
**And** when RED count is ≤2, recommendation is "PROCEED"

---

## Epic 6: Context Override System

**Goal:** Implement the hierarchy of truth that prioritizes user documents over market data.

**Status:** LOGIC DEFINED (in prompts, needs testing)

### Story 6.1: Document Type Detection

As the Context Override System,
I want to identify document types from user uploads,
So that I know how to extract relevant facts.

**Acceptance Criteria:**

**Given** a user uploads a document
**When** I analyze its content
**Then** I identify it as: Tax Abatement, Rent Roll, Appraisal, or Other
**And** I apply the appropriate extraction rules

### Story 6.2: Fact Extraction Engine

As the Context Override System,
I want to extract override facts from documents,
So that specific criteria can be updated with property-specific data.

**Acceptance Criteria:**

**Given** a Tax Abatement document
**When** I extract facts
**Then** I find: abatement percentage, duration, effective date
**And** I map this to criterion sub_13 (Taxes/Fees)

### Story 6.3: Override Application

As the Logic Engine,
I want to apply extracted facts over market data,
So that user documents take precedence in evaluation.

**Acceptance Criteria:**

**Given** market data shows 2.3% tax rate
**When** user document shows 0% abatement for 10 years
**Then** Taxes/Fees criterion uses 0%
**And** `override_applied` is true
**And** `override_document` cites the specific file

---

## Epic 7: PDF Generation Service

**Goal:** Generate professional-quality PDF reports via PDF Noodle API.

**Status:** COMPLETE (PDF Noodle API integration, HTML-to-PDF with signed URLs)

### Story 7.1: FastAPI Application Setup

As a developer,
I want a FastAPI application for PDF generation,
So that n8n can request PDFs via HTTP.

**Acceptance Criteria:**

**Given** the pdf-service is running
**When** I access /health endpoint
**Then** I receive a 200 OK response
**And** the service is ready to accept requests

### Story 7.2: Heat Map PDF Generator

As the PDF Service,
I want to generate a grid-format Heat Map PDF,
So that users see all 30 criteria at a glance.

**Acceptance Criteria:**

**Given** I receive a valid heat map JSON (30 items)
**When** I generate the Heat Map PDF
**Then** it displays a color-coded grid (Green/Yellow/Red)
**And** includes summary statistics and recommendation badge

### Story 7.3: Investment Brief PDF Generator

As the PDF Service,
I want to generate a narrative-format Investment Brief,
So that users get detailed analysis with citations.

**Acceptance Criteria:**

**Given** I receive a valid heat map JSON
**When** I generate the Investment Brief PDF
**Then** it includes: executive summary, section-by-section analysis
**And** source citations are in footnotes
**And** final recommendation is clearly stated with justification

### Story 7.4: PDF Storage and Retrieval

As the PDF Service,
I want to store PDFs and provide download URLs,
So that users can retrieve their reports.

**Acceptance Criteria:**

**Given** PDFs are generated
**When** I store them
**Then** unique filenames are created (sanitized)
**And** download URLs are returned in response
**And** files older than 24 hours are auto-deleted

---

## Epic 8: Frontend Integration

**Goal:** Build the user interface for property input and result display.

**Status:** NOT STARTED (future phase)

### Story 8.1: Property Input Form

As an Acquisition Manager,
I want a web form to enter property details,
So that I can initiate an analysis.

**Acceptance Criteria:**

**Given** I access the web application
**When** I view the input form
**Then** I see fields for: Property Address (with autocomplete), Deal Name
**And** a file upload area for context documents

### Story 8.2: File Upload Component

As an Acquisition Manager,
I want to upload PDF/TXT documents,
So that my property-specific data overrides market data.

**Acceptance Criteria:**

**Given** I have context documents (tax abatement, rent roll)
**When** I upload files
**Then** files are validated (PDF, TXT, max 10MB each)
**And** upload progress is displayed
**And** files are attached to the analysis request

### Story 8.3: Analysis Progress Indicator

As an Acquisition Manager,
I want to see analysis progress,
So that I know the system is working.

**Acceptance Criteria:**

**Given** I submit an analysis request
**When** processing begins
**Then** I see a progress indicator with stages
**And** estimated time remaining is displayed

### Story 8.4: Results Display and Download

As an Acquisition Manager,
I want to view and download my analysis results,
So that I can review and share with my team.

**Acceptance Criteria:**

**Given** analysis is complete
**When** I view the results page
**Then** I see the recommendation (NO-GO/CAUTION/PROCEED)
**And** I can download Heat Map PDF and Investment Brief PDF
**And** I can view a summary of key findings

---

## Epic 9: Testing & Quality Assurance

**Goal:** Validate all logic paths and ensure system reliability.

**Status:** GAUNTLET COMPLETE (7/7 tests passing)

### Story 9.1: Ghost Town Test

As a QA Engineer,
I want to test rejection of low-population areas,
So that fundamentally flawed markets are flagged.

**Acceptance Criteria:**

**Given** a property in a <10,000 population area
**When** the analysis completes
**Then** msa_1 (Population Size) is RED
**And** reasoning explains the threshold violation

### Story 9.2: War Zone Test

As a QA Engineer,
I want to test flagging of high-crime areas,
So that dangerous locations are identified.

**Acceptance Criteria:**

**Given** a property in a high-crime district (>MSA average)
**When** the analysis completes
**Then** sub_1 (Crime Rate) is RED
**And** reasoning cites the crime statistics

### Story 9.3: Context Override Test

As a QA Engineer,
I want to test that user documents override market data,
So that property-specific facts take precedence.

**Acceptance Criteria:**

**Given** a high-tax market with user-uploaded tax abatement
**When** the analysis completes
**Then** sub_13 (Taxes/Fees) is GREEN
**And** `override_applied` is true
**And** `override_document` cites the user file

### Story 9.4: Completeness Validation Test

As a QA Engineer,
I want to verify the heat map contains exactly 30 items,
So that no criteria are skipped.

**Acceptance Criteria:**

**Given** any analysis
**When** I validate the heat map
**Then** array length is exactly 30
**And** all MSA IDs (msa_1-16) are present
**And** all Sub-Market IDs (sub_1-14) are present

### Story 9.5: Goldilocks Logic Tests

As a QA Engineer,
I want to test Goldilocks logic for amenities and vacancy,
So that "sweet spot" evaluation works correctly.

**Acceptance Criteria:**

**Given** amenities at various distances
**When** distance is <0.25 mi, result is RED
**And** when distance is 1-2 mi, result is GREEN
**And** when distance is >2 mi, result is YELLOW or RED
**And** given vacancy rates, 4-6% is GREEN, <3% is YELLOW, >7% is RED

### Story 9.6: Recommendation Threshold Test

As a QA Engineer,
I want to test recommendation calculation,
So that thresholds are applied correctly.

**Acceptance Criteria:**

**Given** a heat map with 6 RED flags
**When** recommendation is calculated
**Then** result is "NO-GO"
**And** given 4 RED flags, result is "CAUTION"
**And** given 2 RED flags, result is "PROCEED"

---

## Epic 10: Deployment & Operations

**Goal:** Deploy the system to production and establish monitoring.

**Status:** NOT STARTED

### Story 10.1: PDF Service Containerization

As a DevOps Engineer,
I want to containerize the PDF service,
So that it can be deployed consistently across environments.

**Acceptance Criteria:**

**Given** the Dockerfile in pdf-service/
**When** I build the image
**Then** the container runs successfully
**And** /health endpoint responds
**And** /generate-pdf endpoint accepts requests

### Story 10.2: n8n Cloud/Self-Hosted Setup

As a DevOps Engineer,
I want to deploy n8n with the main workflow,
So that the orchestration layer is production-ready.

**Acceptance Criteria:**

**Given** n8n is deployed (Cloud or Docker)
**When** I import main-workflow.json
**Then** all nodes are configured correctly
**And** credentials are set up for Perplexity, Gemini, Google Drive

### Story 10.3: Cloud Storage Configuration

As a DevOps Engineer,
I want to configure cloud storage for PDFs,
So that generated reports are accessible and secure.

**Acceptance Criteria:**

**Given** Google Cloud Storage or S3 is configured
**When** PDFs are generated
**Then** they are uploaded to the storage bucket
**And** signed URLs are generated for download
**And** retention policy (24 hours) is enforced

### Story 10.4: Monitoring and Alerting

As a DevOps Engineer,
I want to monitor system health and performance,
So that issues are detected and resolved quickly.

**Acceptance Criteria:**

**Given** the system is in production
**When** I access the monitoring dashboard
**Then** I see: API response times, error rates, queue depth
**And** alerts fire when thresholds are exceeded
**And** logs are aggregated for debugging

---

## Implementation Priority

| Phase | Epics | Timeline |
|-------|-------|----------|
| Phase 1 (MVP Core) | 1, 2, 3, 4, 5, 6, 7, 9 | Current |
| Phase 2 (Frontend) | 8 | Next |
| Phase 3 (Production) | 10 | After MVP validation |

---

_Document generated: 2026-01-18_
_Based on: PRD.md, ARCHITECTURE.md, project-context.md_
