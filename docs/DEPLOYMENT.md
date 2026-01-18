# Deployment Guide
## AI Multifamily Deep Research & Decision Engine

**Version**: 1.0
**Last Updated**: January 18, 2026

---

## Overview

This guide covers deploying the complete system from development to production. The architecture consists of three main components:
1. **n8n Orchestrator** - Workflow engine
2. **PDF Generation Service** - Python FastAPI application
3. **Frontend** - React application (Lovable.dev)

---

## Prerequisites

### Required Accounts
- [ ] Google Cloud Platform (for Vertex AI + Cloud Storage)
- [ ] Perplexity API account
- [ ] n8n instance (cloud or self-hosted)
- [ ] Domain name (for production)

### Required Tools
- Docker Desktop or Docker CLI
- kubectl (for Kubernetes deployment)
- gcloud CLI (for GCP)
- Node.js 18+ (for frontend)
- Python 3.11+ (for local PDF service testing)

---

## Part 1: Local Development Setup

### 1.1 Clone Repository

```bash
git clone https://github.com/your-org/mf-msa-analyzer.git
cd mf-msa-analyzer
```

### 1.2 Setup PDF Service Locally

```bash
cd pdf-service

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PDF_OUTPUT_DIR=/tmp/pdf-output
export PDF_SERVICE_BASE_URL=http://localhost:8000

# Run service
uvicorn app.main:app --reload --port 8000
```

**Test endpoint**:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-01-18T12:00:00.000Z"}
```

### 1.3 Setup n8n Locally (Docker)

```bash
# Create directory for n8n data
mkdir -p ~/.n8n

# Run n8n in Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=password \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Access n8n**: http://localhost:5678

### 1.4 Import Workflow

1. Open n8n UI (http://localhost:5678)
2. Login (admin / password)
3. Click "Workflows" → "Import from File"
4. Select `n8n/workflows/main-workflow.json`
5. Click "Import"

### 1.5 Configure Credentials

#### Google Drive OAuth2
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`
4. Copy Client ID and Client Secret
5. In n8n: Credentials → Add → Google Drive OAuth2 API
6. Paste credentials and authorize

#### Google Vertex AI
1. In Google Cloud Console, enable Vertex AI API
2. Create service account with "Vertex AI User" role
3. Download JSON key file
4. In n8n: Credentials → Add → Google Vertex AI OAuth2 API
5. Upload service account JSON

#### Perplexity API
```bash
# Set environment variable
export PERPLEXITY_API_KEY=your-api-key-here
```

In n8n, reference as `{{ $env.PERPLEXITY_API_KEY }}`

### 1.6 Upload Immutable Laws PDFs

1. Upload `MSA-Criteria.pdf` and `SubMarket-Criteria.pdf` to Google Drive
2. Get file IDs from shareable links
3. Set environment variables in n8n:
   ```bash
   export MSA_CRITERIA_FILE_ID=your-file-id
   export SUBMARKET_CRITERIA_FILE_ID=your-file-id
   ```

### 1.7 Test End-to-End

```bash
curl -X POST http://localhost:5678/webhook/analyze-property \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Austin, TX 78701",
    "deal_name": "Test Property",
    "context_files": []
  }'
```

---

## Part 2: Production Deployment

### 2.1 Deploy PDF Service to Google Cloud Run

#### Step 1: Build Docker Image

```bash
cd pdf-service

# Build image
docker build -t gcr.io/YOUR-PROJECT-ID/pdf-service:latest .

# Test locally
docker run -p 8000:8000 \
  -e PDF_OUTPUT_DIR=/app/output \
  gcr.io/YOUR-PROJECT-ID/pdf-service:latest
```

#### Step 2: Push to Google Container Registry

```bash
# Authenticate with GCP
gcloud auth configure-docker

# Push image
docker push gcr.io/YOUR-PROJECT-ID/pdf-service:latest
```

#### Step 3: Deploy to Cloud Run

```bash
gcloud run deploy pdf-service \
  --image gcr.io/YOUR-PROJECT-ID/pdf-service:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars PDF_SERVICE_BASE_URL=https://pdf-service-xxxxx-uc.a.run.app
```

**Get service URL**:
```bash
gcloud run services describe pdf-service --region us-central1 --format 'value(status.url)'
```

Output: `https://pdf-service-xxxxx-uc.a.run.app`

**Update n8n**:
Set `PDF_SERVICE_URL` environment variable to this URL.

### 2.2 Deploy n8n to Production

#### Option A: n8n Cloud (Recommended for MVP)

1. Sign up at [n8n.cloud](https://n8n.cloud)
2. Create new instance
3. Import workflow from JSON
4. Configure credentials (same as local)
5. Set environment variables in cloud dashboard

**Advantages**:
- Managed infrastructure
- Automatic backups
- Built-in monitoring
- 99.9% uptime SLA

**Cost**: ~$50-100/month

#### Option B: Self-Hosted on Kubernetes

**Prerequisites**:
- GKE cluster (or AWS EKS, Azure AKS)
- kubectl configured

**Deployment**:

```bash
# Create namespace
kubectl create namespace n8n

# Create secret for database
kubectl create secret generic n8n-db \
  --from-literal=password=STRONG-PASSWORD \
  -n n8n

# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml -n n8n

# Deploy n8n
kubectl apply -f k8s/n8n-deployment.yaml -n n8n

# Expose via LoadBalancer
kubectl apply -f k8s/n8n-service.yaml -n n8n

# Get external IP
kubectl get svc n8n -n n8n
```

**k8s/n8n-deployment.yaml** (example):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
spec:
  replicas: 2
  selector:
    matchLabels:
      app: n8n
  template:
    metadata:
      labels:
        app: n8n
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        ports:
        - containerPort: 5678
        env:
        - name: DB_TYPE
          value: postgresdb
        - name: DB_POSTGRESDB_HOST
          value: postgres
        - name: DB_POSTGRESDB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: n8n-db
              key: password
        - name: N8N_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: encryption-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### 2.3 Setup Google Cloud Storage

```bash
# Create bucket for PDFs
gsutil mb -l us-central1 gs://mf-analyzer-pdfs

# Set lifecycle rule (delete after 24 hours)
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 1}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://mf-analyzer-pdfs

# Make bucket private (no public access)
gsutil iam ch allUsers:objectViewer gs://mf-analyzer-pdfs
```

**Update PDF Service**:
Modify `app/main.py` to upload PDFs to GCS instead of local filesystem.

```python
from google.cloud import storage

def upload_to_gcs(local_path, bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    return blob.public_url
```

### 2.4 Setup CDN (Optional)

For faster PDF delivery:

```bash
# Enable Cloud CDN for Cloud Storage bucket
gcloud compute backend-buckets create mf-analyzer-backend \
  --gcs-bucket-name=mf-analyzer-pdfs

gcloud compute url-maps create mf-analyzer-cdn \
  --default-backend-bucket=mf-analyzer-backend

gcloud compute target-http-proxies create mf-analyzer-proxy \
  --url-map=mf-analyzer-cdn

gcloud compute forwarding-rules create mf-analyzer-rule \
  --global \
  --target-http-proxy=mf-analyzer-proxy \
  --ports=80
```

### 2.5 Deploy Frontend (Lovable.dev)

1. Push code to GitHub repository
2. Connect repository to Lovable.dev
3. Set environment variables:
   ```
   VITE_N8N_WEBHOOK_URL=https://your-n8n.com/webhook/analyze-property
   ```
4. Deploy

**Custom domain**:
```bash
# In Lovable dashboard
Settings → Domains → Add Custom Domain
Enter: app.yourdomain.com
```

---

## Part 3: Configuration Management

### 3.1 Environment Variables

**Production Environment Variables**:

```bash
# n8n
N8N_HOST=https://n8n.yourdomain.com
N8N_ENCRYPTION_KEY=<32-char-random-string>
WEBHOOK_URL=https://n8n.yourdomain.com

# Google Cloud
MSA_CRITERIA_FILE_ID=1abc...xyz
SUBMARKET_CRITERIA_FILE_ID=1def...uvw
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# APIs
PERPLEXITY_API_KEY=pplx-xxxxx
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1

# PDF Service
PDF_SERVICE_URL=https://pdf-service-xxxxx-uc.a.run.app
PDF_OUTPUT_DIR=/app/output
PDF_SERVICE_BASE_URL=https://cdn.yourdomain.com
```

**Store secrets in**:
- Google Secret Manager (recommended)
- AWS Secrets Manager
- HashiCorp Vault

### 3.2 Secure Secrets Management

```bash
# Create secret in Google Secret Manager
echo -n "pplx-xxxxx" | gcloud secrets create perplexity-api-key \
  --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding perplexity-api-key \
  --member="serviceAccount:SERVICE-ACCOUNT@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Reference in Cloud Run
gcloud run services update pdf-service \
  --update-secrets=PERPLEXITY_API_KEY=perplexity-api-key:latest
```

---

## Part 4: Monitoring & Logging

### 4.1 Setup Cloud Logging

**Cloud Run (automatic)**:
Logs are automatically sent to Cloud Logging.

**View logs**:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pdf-service" \
  --limit 50 \
  --format json
```

**n8n logs**:
```bash
kubectl logs -f deployment/n8n -n n8n
```

### 4.2 Setup Monitoring

**Metrics to track**:
- Request count
- Error rate
- Latency (p50, p95, p99)
- PDF generation time

**Cloud Monitoring Dashboard**:
```bash
# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

**Alert policies**:
```bash
# Alert on high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL-ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=60s
```

### 4.3 Setup Uptime Checks

```bash
# Create uptime check for PDF service
gcloud monitoring uptime create pdf-service-health \
  --resource-type=uptime-url \
  --host=pdf-service-xxxxx-uc.a.run.app \
  --path=/health \
  --check-interval=60s
```

---

## Part 5: Scaling & Performance

### 5.1 Auto-Scaling Configuration

**Cloud Run** (automatic):
- Min instances: 0 (cold start acceptable for MVP)
- Max instances: 10
- Concurrency: 80 requests per instance

**Optimize cold starts**:
```bash
gcloud run services update pdf-service \
  --min-instances=1  # Keep 1 instance warm
```

### 5.2 Caching Strategy

**Perplexity results caching**:
```python
import redis
import hashlib

redis_client = redis.Redis(host='redis-server', port=6379)

def get_cached_research(address):
    cache_key = hashlib.md5(address.encode()).hexdigest()
    cached = redis_client.get(f"research:{cache_key}")
    if cached:
        return json.loads(cached)
    return None

def cache_research(address, data):
    cache_key = hashlib.md5(address.encode()).hexdigest()
    redis_client.setex(
        f"research:{cache_key}",
        86400,  # 24 hour TTL
        json.dumps(data)
    )
```

### 5.3 Database Optimization (Future)

When adding user accounts:
- Use connection pooling (SQLAlchemy)
- Add database read replicas
- Index frequently queried fields

---

## Part 6: Backup & Disaster Recovery

### 6.1 n8n Backups

**Automated backups** (if self-hosted):
```bash
# Backup PostgreSQL database
kubectl exec -n n8n postgres-0 -- pg_dump -U n8n > backup-$(date +%Y%m%d).sql

# Upload to GCS
gsutil cp backup-$(date +%Y%m%d).sql gs://n8n-backups/
```

**Backup schedule**: Daily at 2 AM UTC

### 6.2 Workflow Versioning

Export workflow JSON after each change:
```bash
# In n8n UI
Workflows → Select workflow → Download
```

Commit to Git:
```bash
git add n8n/workflows/main-workflow.json
git commit -m "Update workflow: Add error handling"
git push
```

### 6.3 Disaster Recovery Plan

**RTO** (Recovery Time Objective): 4 hours
**RPO** (Recovery Point Objective): 24 hours

**Recovery steps**:
1. Restore n8n database from latest backup (30 min)
2. Redeploy Cloud Run services (15 min)
3. Import workflow from Git (5 min)
4. Configure credentials (30 min)
5. Test end-to-end (2 hours)

---

## Part 7: Security Hardening

### 7.1 Network Security

**Cloud Run**:
- Enable VPC connector (isolate from public internet)
- Use Cloud Armor for DDoS protection

```bash
gcloud run services update pdf-service \
  --vpc-connector=my-connector \
  --vpc-egress=private-ranges-only
```

### 7.2 Authentication

**n8n webhook protection**:
```bash
# Set webhook authentication
export N8N_WEBHOOK_AUTH_HEADER=X-API-Key
export N8N_WEBHOOK_AUTH_VALUE=<strong-random-key>
```

**Validate in workflow**:
Add validation node to check header before processing.

### 7.3 Rate Limiting

**Cloud Armor policy**:
```bash
gcloud compute security-policies create rate-limit-policy \
  --description="Rate limit to 100 req/min"

gcloud compute security-policies rules create 1000 \
  --security-policy=rate-limit-policy \
  --action=rate-based-ban \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60
```

---

## Part 8: Testing in Production

### 8.1 Smoke Tests

Run after deployment:

```bash
# Test PDF service health
curl https://pdf-service-xxxxx-uc.a.run.app/health

# Test n8n webhook (with dummy data)
curl -X POST https://n8n.yourdomain.com/webhook/analyze-property \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d @tests/test_data/sample_request.json
```

### 8.2 Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 \
  -H "Content-Type: application/json" \
  -p tests/test_data/sample_request.json \
  https://n8n.yourdomain.com/webhook/analyze-property
```

**Expected results**:
- Requests per second: >5
- Mean latency: <120 seconds
- Failed requests: 0

---

## Part 9: Rollback Procedures

### 9.1 Cloud Run Rollback

```bash
# List revisions
gcloud run revisions list --service=pdf-service

# Rollback to previous revision
gcloud run services update-traffic pdf-service \
  --to-revisions=pdf-service-xxxxx=100
```

### 9.2 n8n Workflow Rollback

1. In n8n UI: Workflows → Version History
2. Select previous version
3. Click "Restore"

Or from Git:
```bash
git checkout HEAD~1 -- n8n/workflows/main-workflow.json
# Re-import in n8n UI
```

---

## Part 10: Maintenance

### 10.1 Regular Tasks

**Weekly**:
- Review error logs
- Check API quota usage (Perplexity, Vertex AI)
- Test sample analysis end-to-end

**Monthly**:
- Review and optimize costs
- Update dependencies (npm, pip)
- Rotate API keys

**Quarterly**:
- Review and update criteria thresholds
- Disaster recovery drill
- Security audit

### 10.2 Dependency Updates

```bash
# Update Python dependencies
cd pdf-service
pip list --outdated
pip install -U package-name
pip freeze > requirements.txt

# Update n8n
docker pull n8nio/n8n:latest
kubectl set image deployment/n8n n8n=n8nio/n8n:latest -n n8n
```

---

## Troubleshooting

### Common Issues

**Issue**: PDF generation timeout
**Solution**: Increase Cloud Run timeout to 300 seconds
```bash
gcloud run services update pdf-service --timeout=300
```

**Issue**: n8n webhook returns 502
**Solution**: Check Cloud Run logs for errors
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

**Issue**: Perplexity API rate limit exceeded
**Solution**: Implement caching and request throttling

---

## Support

For deployment issues, contact:
- Email: devops@yourcompany.com
- Slack: #mf-analyzer-support

---

**Document Control**
Author: DevOps Team
Version: 1.0
Last Updated: January 18, 2026
Next Review: April 2026
