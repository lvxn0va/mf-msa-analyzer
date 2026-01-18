# Technical Architecture Document
## AI Multifamily Deep Research & Decision Engine

**Version**: 1.0
**Status**: Implementation Ready
**Last Updated**: January 18, 2026

---

## 1. System Overview

### 1.1 Architecture Philosophy

This system uses a **hybrid architecture** combining:
- **n8n** for visual workflow orchestration (allows non-developers to audit logic)
- **Python FastAPI** for specialized PDF generation
- **Google Gemini** for reasoning and logic application
- **Perplexity Sonar-Pro** for live web research

### 1.2 Design Principles

1. **Separation of Concerns**: Research, logic, and output are distinct stages
2. **Auditability**: Every decision must be traceable to source data
3. **Fail-Safe**: If any component fails, provide clear error messages
4. **Extensibility**: New criteria can be added without rewriting core logic
5. **Cost Efficiency**: Use appropriate model sizes (Haiku for simple, Opus for complex)

---

## 2. System Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Lovable.dev - React)                        │
│  - Property address input                                       │
│  - Deal name input                                              │
│  - Context document upload (PDFs, Excel)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTPS POST
┌─────────────────────────────────────────────────────────────────┐
│                      n8n ORCHESTRATOR                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 1. Webhook Trigger                                        │  │
│  │    - Receives: address, deal_name, context_files         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 2. Context Loader                                         │  │
│  │    - Fetches MSA-Criteria.pdf from Google Drive          │  │
│  │    - Fetches SubMarket-Criteria.pdf from Google Drive    │  │
│  │    - Parses user-uploaded context docs                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 3. Research Agent (Perplexity Sonar-Pro)                 │  │
│  │    - 1-3-5 mile demographic data                         │  │
│  │    - Crime, schools, amenities                           │  │
│  │    - MSA-level economics                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 4. Logic Engine (Google Gemini 2.0 Flash)                │  │
│  │    - Evaluates 30-point criteria                         │  │
│  │    - Applies context override logic                      │  │
│  │    - Outputs JSON heat map                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 5. Validation Node                                        │  │
│  │    - Ensures 30 items in array                           │  │
│  │    - Validates status values (GREEN/YELLOW/RED)          │  │
│  │    - Checks required fields                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│                   PDF GENERATION SERVICE                        │
│                   (Python FastAPI)                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Heat Map PDF Generator (ReportLab)                        │  │
│  │  - Visual grid with traffic lights                       │  │
│  │  - Summary statistics                                    │  │
│  │  - Recommendation                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Investment Brief PDF Generator (ReportLab)                │  │
│  │  - Narrative format                                      │  │
│  │  - Detailed reasoning                                    │  │
│  │  - Citations                                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ PDF URLs
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE (S3/GCS)                           │
│  - Generated PDFs (24-hour retention)                           │
│  - Immutable Laws PDFs (permanent)                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Frontend (Lovable.dev)

**Technology**: React + TypeScript + Tailwind CSS

**Responsibilities**:
- Property address input with autocomplete
- Deal name text input
- Drag-and-drop file upload for context documents
- Progress indicator during analysis
- PDF download links in results view

**API Integration**:
```typescript
interface AnalysisRequest {
  address: string;
  deal_name: string;
  context_files: Array<{
    name: string;
    data: string; // base64
    type: string; // MIME type
  }>;
}

interface AnalysisResponse {
  status: "success" | "error";
  analysis_summary: {
    total_criteria: 30;
    green_count: number;
    yellow_count: number;
    red_count: number;
    recommendation: "NO-GO" | "CAUTION" | "PROCEED";
  };
  heat_map: HeatMapItem[];
  pdf_url: string;
  generated_at: string;
}
```

### 3.2 n8n Orchestrator

**Technology**: n8n (self-hosted or cloud)

**Workflow Nodes**:

#### Node 1: Webhook Trigger
- **Type**: `n8n-nodes-base.webhook`
- **Method**: POST
- **Path**: `/webhook/analyze-property`
- **Input**: JSON body with address, deal_name, context_files

#### Node 2: Extract Input Data
- **Type**: `n8n-nodes-base.set`
- **Purpose**: Parse request body into workflow variables

#### Node 3: Load Criteria PDFs
- **Type**: `n8n-nodes-base.googleDrive` (parallel)
- **Files**:
  - MSA-Criteria.pdf (stored in Google Drive)
  - SubMarket-Criteria.pdf (stored in Google Drive)

#### Node 4: Parse PDFs
- **Type**: `n8n-nodes-base.code`
- **Purpose**: Convert PDFs to text for AI context
- **Library**: PDF.co API or Python pdf2text

#### Node 5: Parse User Context Docs
- **Type**: `n8n-nodes-base.code`
- **Purpose**: Extract text from user uploads
- **Output**: Array of {filename, content, type}

#### Node 6: Perplexity Research Agent
- **Type**: `n8n-nodes-base.httpRequest`
- **URL**: `https://api.perplexity.ai/chat/completions`
- **Model**: `sonar-pro`
- **Input**: Research prompt template + address
- **Output**: Demographic and market data with citations

#### Node 7: Gemini Logic Engine
- **Type**: `@n8n/n8n-nodes-langchain.lmChatGoogleVertex`
- **Model**: `gemini-2.0-flash-exp`
- **Temperature**: 0.1 (deterministic)
- **Max Tokens**: 8000
- **Input**:
  - System prompt (Immutable Laws)
  - User prompt (Research data + Context docs)
- **Output**: 30-point JSON heat map

#### Node 8: Validate Heat Map
- **Type**: `n8n-nodes-base.code`
- **Validations**:
  - Array length = 30
  - All IDs present (msa_1-16, sub_1-14)
  - Status values valid (GREEN/YELLOW/RED)
  - Required fields present

#### Node 9: Generate PDFs
- **Type**: `n8n-nodes-base.httpRequest`
- **URL**: `{PDF_SERVICE_URL}/generate-pdf`
- **Method**: POST
- **Body**: Heat map + deal metadata

#### Node 10: Response
- **Type**: `n8n-nodes-base.respondToWebhook`
- **Body**: Analysis results + PDF URLs

### 3.3 Research Engine (Perplexity)

**API**: Perplexity API
**Model**: `sonar-pro` (with citations)

**Prompt Template**:
```
You are a real estate market research specialist.

TARGET PROPERTY: {address}

Gather the following data with specific citations:

MSA-LEVEL:
- Population (current + 5-year growth)
- Employment (current + 3-year growth)
- Unemployment rate
- Apartment vacancy rate
- ... [full criteria list]

SUB-MARKET (1-3-5 mile radii):
- Crime rate (violent + property per 1000)
- School ratings (GreatSchools)
- Amenities (grocery, retail, parks)
- ... [full criteria list]

For each data point, provide:
1. Value
2. Source (name + year)
3. URL (if web-based)

Output as JSON.
```

**Expected Output**:
```json
{
  "msa_data": {
    "population": {
      "value": "2,200,000",
      "source": "US Census 2024",
      "url": "https://census.gov/..."
    },
    ...
  },
  "submarket_data": {
    "crime_violent_rate": {
      "value": "2.1 per 1000",
      "source": "FBI UCR 2024",
      "comparison_to_msa": "-40%"
    },
    ...
  }
}
```

### 3.4 Logic Engine (Google Gemini)

**API**: Google Vertex AI
**Model**: `gemini-2.0-flash-exp`
**Temperature**: 0.1 (minimize variability)

**System Prompt**: See `/prompts/gemini-system-prompt.txt`

**Key Instructions**:
1. No hallucinations (only use provided data)
2. Context override hierarchy (user docs > research > market data)
3. Goldilocks logic for distance-based criteria
4. Output strict JSON schema

**Token Budget**:
- Input: ~6,000 tokens (context + research)
- Output: ~2,000 tokens (heat map JSON)
- Total: ~8,000 tokens per analysis

**Cost Estimate** (Gemini Flash):
- $0.01 per 1M input tokens
- $0.03 per 1M output tokens
- **Per analysis**: ~$0.0001 (negligible)

### 3.5 PDF Generation Service

**Technology**: Python 3.11 + FastAPI + ReportLab

**Endpoints**:

#### `POST /generate-pdf`
**Input**:
```json
{
  "heat_map": [...30 items...],
  "deal_name": "Sunset Apartments",
  "address": "123 Main St, Austin, TX",
  "research_data": {...}
}
```

**Output**:
```json
{
  "status": "success",
  "heat_map_url": "https://.../HeatMap_20240118.pdf",
  "investment_brief_url": "https://.../InvestmentBrief_20240118.pdf"
}
```

**PDF Generators**:

1. **Heat Map PDF** (`heat_map_pdf.py`):
   - Landscape orientation
   - Table format with color-coded rows
   - Summary statistics
   - Recommendation badge

2. **Investment Brief PDF** (`investment_brief_pdf.py`):
   - Portrait orientation
   - Executive summary
   - Section-by-section analysis
   - Citations in footnotes
   - Disclaimer

**Libraries**:
- ReportLab: PDF generation
- Pillow: Image handling (if needed)
- Pydantic: Request/response validation

### 3.6 Storage

**Options**:
- **Google Cloud Storage** (if using Vertex AI)
- **AWS S3** (if using Bedrock)
- **Local filesystem** (MVP only)

**File Structure**:
```
/storage
├── immutable-laws/
│   ├── MSA-Criteria.pdf
│   └── SubMarket-Criteria.pdf
└── generated-pdfs/
    ├── 2024-01-18/
    │   ├── sunset-apartments_heatmap.pdf
    │   └── sunset-apartments_brief.pdf
    └── ...
```

**Retention Policy**:
- Immutable Laws: Permanent
- Generated PDFs: 24 hours (then auto-delete)

---

## 4. Data Flow

### 4.1 Happy Path

1. User submits analysis request → n8n webhook
2. n8n loads criteria PDFs → Google Drive
3. n8n parses user context docs → Extract text
4. n8n calls Perplexity → Get research data
5. n8n calls Gemini → Evaluate criteria → Output JSON
6. n8n validates JSON → Check 30 items, valid statuses
7. n8n calls PDF service → Generate 2 PDFs
8. n8n returns response → User downloads PDFs

**Total Time**: ~90-180 seconds

### 4.2 Error Handling

**Scenario 1**: Perplexity API timeout
- **Action**: Retry up to 3 times with exponential backoff
- **If still fails**: Return partial analysis with warning

**Scenario 2**: Gemini returns invalid JSON
- **Action**: Log error, re-prompt with explicit JSON format request
- **If still fails**: Return error to user with request ID for support

**Scenario 3**: PDF generation fails
- **Action**: Return heat map JSON to user, log error
- **User can**: Download raw JSON or retry PDF generation

**Scenario 4**: User uploads corrupted document
- **Action**: Skip that document, proceed with others
- **Note**: Flag in response that 1 document failed to parse

---

## 5. Security Architecture

### 5.1 Authentication & Authorization

**MVP**: No user accounts (open access)

**Future** (v2.0):
- OAuth 2.0 with Google/Microsoft
- Role-based access (Viewer, Analyst, Admin)
- API key authentication for integrations

### 5.2 Data Security

**In Transit**:
- All HTTP requests over TLS 1.3
- n8n webhook requires HTTPS

**At Rest**:
- User-uploaded documents encrypted (AES-256)
- Generated PDFs stored in private S3 buckets
- No plaintext credentials in code (use env vars)

**Data Retention**:
- User uploads: Deleted after analysis completes
- Generated PDFs: Deleted after 24 hours
- No PII stored (addresses are not PII under GDPR)

### 5.3 API Security

**Rate Limiting**:
- 100 requests per IP per hour (MVP)
- 1,000 requests per day per IP

**Input Validation**:
- Address: Max 500 characters
- Deal name: Max 200 characters
- File uploads: Max 10MB per file, max 5 files
- Allowed MIME types: PDF, Excel, Word

---

## 6. Scalability & Performance

### 6.1 Current Capacity (MVP)

- **Concurrent analyses**: 5 (n8n workers)
- **Daily throughput**: ~500 analyses
- **Average latency**: 120 seconds

### 6.2 Scaling Strategy

**Horizontal Scaling**:
- Add n8n worker nodes (queue mode)
- Deploy multiple PDF service instances (load balanced)
- Use Redis for distributed caching

**Vertical Scaling**:
- Increase n8n worker memory (8GB → 16GB)
- Optimize PDF generation (parallel rendering)

**Caching**:
- Cache Perplexity results by address hash (24-hour TTL)
- Cache criteria PDFs in memory (no re-fetch)

### 6.3 Performance Optimization

**Bottlenecks**:
1. Perplexity API latency (30-60 seconds)
2. Gemini processing time (20-40 seconds)
3. PDF generation (10-20 seconds)

**Optimizations**:
1. Parallel API calls where possible
2. Pre-warm Gemini context (load criteria once)
3. Use Gemini Flash instead of Pro (4x faster)
4. Async PDF generation (return immediately, email PDF)

---

## 7. Monitoring & Observability

### 7.1 Metrics to Track

**System Health**:
- n8n workflow execution success rate
- Average execution time per stage
- API error rates (Perplexity, Gemini, PDF)

**Business Metrics**:
- Analyses per day
- Average GREEN/YELLOW/RED counts
- Context override usage rate
- PDF download rate

### 7.2 Logging

**n8n**: Built-in execution logs (retain 30 days)

**PDF Service**: Structured JSON logs
```json
{
  "timestamp": "2024-01-18T12:00:00Z",
  "level": "INFO",
  "service": "pdf-generator",
  "analysis_id": "abc123",
  "event": "pdf_generated",
  "duration_ms": 1250
}
```

**Alerting**:
- Slack/email on >10% error rate
- Page on critical failures (database down, etc.)

---

## 8. Deployment Architecture

### 8.1 MVP Deployment

**n8n**:
- Deployed on DigitalOcean Droplet (2 vCPU, 4GB RAM)
- Docker container
- Managed PostgreSQL database

**PDF Service**:
- Deployed on Cloud Run (Google Cloud)
- Auto-scaling (0-10 instances)
- Triggered via HTTP

**Storage**:
- Google Cloud Storage bucket (private)

### 8.2 Production Deployment (Future)

**n8n**:
- Kubernetes cluster (3 nodes)
- Horizontal pod autoscaling
- Redis for queue management

**PDF Service**:
- Kubernetes deployment (5 replicas)
- Load balanced
- CDN for PDF delivery

**Database**:
- Cloud SQL (PostgreSQL) for user data
- Redis for caching

---

## 9. Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| Orchestrator | n8n | 1.0+ | Visual workflow, no-code auditing |
| Logic Engine | Google Gemini Flash | 2.0 | Fast, cost-effective reasoning |
| Research | Perplexity Sonar-Pro | Latest | Live web search with citations |
| PDF Service | Python FastAPI | 3.11+ | Async, high performance |
| PDF Library | ReportLab | 4.0+ | Professional PDF generation |
| Storage | Google Cloud Storage | - | Low cost, high availability |
| Frontend | Lovable.dev (React) | - | Rapid prototyping |

---

## 10. API Reference

### 10.1 n8n Webhook

**Endpoint**: `POST /webhook/analyze-property`

**Request**:
```json
{
  "address": "123 Main St, Austin, TX 78701",
  "deal_name": "Sunset Apartments",
  "context_files": [
    {
      "name": "tax_abatement.pdf",
      "data": "base64_encoded_content",
      "type": "application/pdf"
    }
  ]
}
```

**Response**:
```json
{
  "status": "success",
  "analysis_id": "abc123",
  "deal_name": "Sunset Apartments",
  "address": "123 Main St, Austin, TX 78701",
  "analysis_summary": {
    "total_criteria": 30,
    "green_count": 18,
    "yellow_count": 8,
    "red_count": 4,
    "recommendation": "CAUTION"
  },
  "heat_map": [...],
  "pdf_url": "https://storage.../heatmap.pdf",
  "investment_brief_url": "https://storage.../brief.pdf",
  "generated_at": "2024-01-18T12:00:00Z"
}
```

### 10.2 PDF Service

**Endpoint**: `POST /generate-pdf`

**Request**: Same as heat_map array + metadata

**Response**:
```json
{
  "status": "success",
  "heat_map_url": "https://.../heatmap.pdf",
  "investment_brief_url": "https://.../brief.pdf"
}
```

---

**Document Control**
Author: Engineering Team
Reviewed By: CTO
Version: 1.0
Next Review: Q2 2026
