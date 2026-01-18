# AI Multifamily Deep Research & Decision Engine

Version: 1.0 (MVP)
Status: Ready for Build
Architecture: Hybrid (n8n Orchestrator + PDF Service)

## Executive Summary

A web-based "Deep Research & Decision Engine" for multifamily real estate investors. It automates the top-of-funnel due diligence phase by performing live 1-3-5 mile demographic analysis and evaluating deals against strict, proprietary "Secret Sauce" criteria.

**Core Value**: Reduces weeks of manual research to minutes while enforcing institutional discipline to prevent "deal fever."

## System Architecture

### Technology Stack

- **Frontend**: Lovable.dev (React) - Handles file uploads and input forms
- **Orchestrator**: n8n (Self-hosted or Cloud) - Manages workflow state
- **Reasoning Engine**: Google Gemini 3 Pro (via Google Vertex AI) - Logic application
- **Research Engine**: Perplexity Sonar-Pro (via HTTP Request) - Live web scraping
- **Storage**: Google Drive or AWS S3 - Stores "Immutable Law" PDFs
- **Output**: PDF Generation Service (Python FastAPI) - Renders styled PDFs

### Key Components

1. **Context Container Logic**: Hierarchical separation of Macro (MSA) and Micro (Sub-market) analysis
2. **Deep Research Agent**: Automated demographic and market data harvesting
3. **30-Point Logic Engine**: Evaluates ALL criteria with Green/Yellow/Red status
4. **Context Override System**: User-uploaded documents take precedence
5. **PDF Generation**: Professional Decision Heat Map and Investment Brief

## Directory Structure

```
/mf-msa-analyzer
├── n8n/
│   ├── workflows/               # n8n workflow JSON exports
│   ├── credentials/             # Credential configuration templates
│   └── README.md               # n8n setup instructions
├── pdf-service/
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── models.py          # Pydantic data models
│   │   ├── generators/        # PDF generation logic
│   │   └── templates/         # PDF templates
│   ├── requirements.txt
│   └── Dockerfile
├── schemas/
│   ├── heat-map-schema.json   # 30-Point Heat Map JSON Schema
│   ├── msa-criteria.json      # MSA-level criteria definitions
│   └── submarket-criteria.json # Sub-market criteria definitions
├── prompts/
│   ├── gemini-system-prompt.txt
│   ├── perplexity-research-prompt.txt
│   └── context-override-logic.txt
├── tests/
│   ├── test_gauntlet.py       # Automated test suite
│   └── test_data/             # Test case data
├── docs/
│   ├── PRD.md                 # Product Requirements Document
│   ├── ARCHITECTURE.md        # Technical Architecture
│   └── DEPLOYMENT.md          # Deployment Guide
└── README.md
```

## Quick Start

### Prerequisites

- n8n instance (self-hosted or cloud)
- Google Vertex AI API access
- Perplexity API key
- Python 3.11+
- Docker (optional)

### Setup Steps

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd mf-msa-analyzer
   ```

2. **Configure n8n**
   ```bash
   cd n8n
   # Import workflow from workflows/main-workflow.json
   # Configure credentials using credentials/template.json
   ```

3. **Setup PDF Service**
   ```bash
   cd pdf-service
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. **Run Tests**
   ```bash
   pytest tests/test_gauntlet.py -v
   ```

## User Workflow

1. **Input Phase**
   - Enter Property Address and Deal Name
   - Upload context documents (Tax Abatement, Rent Rolls, etc.)

2. **Processing Phase**
   - System identifies Macro (MSA) and Micro (Sub-market) context
   - AI performs live research (1-3-5 mile demographics)
   - Logic Engine evaluates against 30-Point Criteria

3. **Output Phase**
   - Download Decision Heat Map (Grid PDF)
   - Download Investment Brief (Narrative PDF)

## The 30-Point Criteria

### MSA Criteria (16 Points)
- Population Size, Growth, Employment, Income
- Migration, Diversity, Environmental Risk
- Unemployment, Vacancy, Cap Rate, Permits
- Absorption, Landlord Laws, Affordability, Proximity

### Sub-Market Criteria (14 Points)
- Crime Rate, School Ratings, Amenities
- Transport Access, Path of Growth, Zoning
- Renter Density, MF Asset Clustering
- Taxes/Fees, Appreciation, Government Stability

## Testing Strategy

### Automated Test Cases (The Gauntlet)

1. **Ghost Town Test**: Address in <10k population → NO-GO Signal
2. **War Zone Test**: High-crime district → RED on Crime Metric
3. **Context Override Test**: Tax abatement PDF → GREEN on Taxes/Fees
4. **Completeness Check**: JSON contains exactly 30 items

## API Endpoints

### n8n Webhook
```
POST /webhook/analyze-property
Content-Type: application/json

{
  "address": "123 Main St, Austin, TX",
  "deal_name": "Sunset Apartments",
  "context_files": ["base64_encoded_pdf_1", "base64_encoded_pdf_2"]
}
```

### PDF Service
```
POST /generate-pdf
Content-Type: application/json

{
  "heat_map": [...30 criteria objects...],
  "deal_name": "Sunset Apartments",
  "address": "123 Main St, Austin, TX"
}
```

## Contributing

This project follows the BMad 4.0 agent methodology:
- **Architect**: Establish file structure and API connections
- **Developer**: Build n8n workflows and services
- **QA**: Verify "Secret Sauce" logic with test cases

## License

Proprietary - All Rights Reserved

## Support

For issues and questions, contact the development team.
