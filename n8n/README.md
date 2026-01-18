# n8n Workflow Configuration

## Overview

This directory contains the n8n workflow configuration for the Multifamily Deep Research Engine. The workflow orchestrates the entire analysis pipeline from property input to PDF generation.

## Workflow Architecture

### Node Flow

1. **Webhook Trigger** - Receives property analysis requests
2. **Extract Input Data** - Parses address, deal name, and context files
3. **Load MSA Criteria PDF** - Fetches MSA-level criteria from Google Drive
4. **Load Sub-Market Criteria PDF** - Fetches sub-market criteria from Google Drive
5. **Parse Criteria PDFs** - Converts PDFs to text for AI processing
6. **Parse User Context Docs** - Extracts text from user-uploaded documents
7. **Load Research Prompt** - Prepares Perplexity research query
8. **Perplexity Research Agent** - Gathers live market data
9. **Gemini Logic Engine** - Evaluates 30-point criteria
10. **Validate Heat Map JSON** - Ensures output quality
11. **Generate Investment Brief PDF** - Creates final deliverables
12. **Webhook Response** - Returns results to client

## Setup Instructions

### Prerequisites

- n8n instance (v1.0.0 or higher)
- Google Cloud Platform account
- Perplexity API account
- PDF generation service deployed

### Step 1: Import Workflow

1. Open your n8n instance
2. Click "Workflows" → "Import from File"
3. Select `workflows/main-workflow.json`
4. Click "Import"

### Step 2: Configure Credentials

#### Google Drive OAuth2

1. Go to Credentials → Add Credential
2. Select "Google Drive OAuth2 API"
3. Name: `Google Drive Account`
4. Enter your OAuth2 credentials:
   - Client ID: `your-client-id`
   - Client Secret: `your-client-secret`
5. Click "Connect my account" and authorize

#### Google Vertex AI OAuth2

1. Go to Credentials → Add Credential
2. Select "Google Vertex AI OAuth2 API"
3. Name: `Google Vertex AI Account`
4. Enter your service account JSON or OAuth2 credentials
5. Save

#### Perplexity API Key

1. Set environment variable:
   ```bash
   export PERPLEXITY_API_KEY=your-api-key
   ```

### Step 3: Configure Environment Variables

Set these environment variables in your n8n instance:

```bash
# Google Drive File IDs for Immutable Laws PDFs
MSA_CRITERIA_FILE_ID=your-msa-criteria-file-id
SUBMARKET_CRITERIA_FILE_ID=your-submarket-criteria-file-id

# Perplexity API
PERPLEXITY_API_KEY=your-perplexity-api-key

# PDF Service Endpoint
PDF_SERVICE_URL=http://localhost:8000
```

To find Google Drive File IDs:
1. Upload your criteria PDFs to Google Drive
2. Right-click → Get Link
3. Extract ID from URL: `https://drive.google.com/file/d/{FILE_ID}/view`

### Step 4: Activate Workflow

1. Open the imported workflow
2. Click "Active" toggle in top-right
3. Note the webhook URL (e.g., `https://your-n8n.com/webhook/analyze-property`)

## Testing the Workflow

### Test Request

```bash
curl -X POST https://your-n8n.com/webhook/analyze-property \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Austin, TX 78701",
    "deal_name": "Sunset Apartments",
    "context_files": [
      {
        "name": "tax_abatement.pdf",
        "data": "base64_encoded_pdf_data",
        "type": "application/pdf"
      }
    ]
  }'
```

### Expected Response

```json
{
  "status": "success",
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
  "pdf_url": "https://your-pdf-service.com/downloads/sunset-apartments-brief.pdf",
  "generated_at": "2024-01-18T12:00:00Z"
}
```

## Workflow Execution Monitoring

### View Executions

1. Click "Executions" in left sidebar
2. Filter by workflow: "Multifamily Deep Research Engine"
3. Click on execution to view detailed logs

### Common Issues

#### Issue: "Failed to load criteria PDFs"
**Solution**: Verify Google Drive file IDs and credentials

#### Issue: "Perplexity API rate limit"
**Solution**: Add rate limiting node or upgrade Perplexity plan

#### Issue: "Gemini timeout"
**Solution**: Increase timeout in HTTP request settings to 120 seconds

#### Issue: "Invalid heat map JSON"
**Solution**: Check Gemini system prompt and response format

## Customization

### Modifying System Prompts

1. Edit files in `/prompts/` directory
2. Workflow will load updated prompts on next execution
3. No need to reimport workflow

### Adding New Criteria

1. Update `schemas/msa-criteria.json` or `schemas/submarket-criteria.json`
2. Update Immutable Laws PDFs in Google Drive
3. Update validation in "Validate Heat Map JSON" node (change `maxItems: 30` to new count)

### Changing AI Models

#### Switch to OpenAI GPT-4

1. Replace "Gemini Logic Engine" node with "OpenAI Chat Model" node
2. Update credentials
3. Adjust token limits (GPT-4: 8000 tokens)

#### Switch to Claude

1. Replace with "Anthropic Chat Model" node
2. Use Claude 3 Opus for best reasoning
3. Adjust system prompt for Claude format

## Performance Optimization

### Parallel Processing

The workflow executes these nodes in parallel:
- Load MSA Criteria PDF
- Load Sub-Market Criteria PDF
- Parse User Context Docs
- Load Research Prompt Template

### Caching Strategy

To reduce API costs, implement caching:

1. Add "Redis" node after Perplexity Research
2. Cache research results by address hash
3. TTL: 24 hours

Example cache key: `md5(address)_research_data`

### Batch Processing

For multiple properties:

1. Modify webhook to accept array of addresses
2. Add "Loop Over Items" node
3. Process properties sequentially or in batches

## Security Considerations

### API Key Management

- Never hardcode API keys in workflow
- Use environment variables
- Rotate keys quarterly

### Data Privacy

- User-uploaded documents contain sensitive financial data
- Enable workflow encryption
- Set execution data retention to 7 days

### Access Control

- Restrict webhook endpoint with API key header
- Example: `X-API-Key: your-secret-key`
- Add validation node at start of workflow

## Deployment

### Production Checklist

- [ ] All credentials configured
- [ ] Environment variables set
- [ ] Workflow tested with sample data
- [ ] Error handling implemented
- [ ] Monitoring/alerting configured
- [ ] Backup strategy in place
- [ ] Documentation updated

### Scaling Considerations

- Use n8n queue mode for high throughput
- Deploy multiple n8n workers
- Use Redis for distributed caching
- Monitor execution times and optimize slow nodes

## Support

For issues with this workflow:
1. Check execution logs in n8n
2. Review error messages
3. Consult n8n documentation: https://docs.n8n.io
4. Contact development team

## Version History

- **v1.0.0** (2024-01-18): Initial release
  - 30-point criteria evaluation
  - Context override logic
  - PDF generation integration
