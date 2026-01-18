"""
FastAPI application for generating multifamily investment PDFs
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime

from app.models import HeatMapItem, PDFGenerationRequest, PDFGenerationResponse
from app.generators.heat_map_pdf import generate_heat_map_pdf
from app.generators.investment_brief_pdf import generate_investment_brief_pdf

app = FastAPI(
    title="Multifamily Research Engine - PDF Service",
    description="Generates Decision Heat Maps and Investment Briefs",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output directory for generated PDFs
OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cleanup old PDFs (older than 24 hours)
def cleanup_old_pdfs():
    """Remove PDFs older than 24 hours"""
    current_time = datetime.now().timestamp()
    for filename in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > 86400:  # 24 hours in seconds
                os.remove(filepath)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Multifamily Research Engine - PDF Service",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "output_dir": OUTPUT_DIR,
        "output_dir_exists": os.path.exists(OUTPUT_DIR)
    }

@app.post("/generate-pdf", response_model=PDFGenerationResponse)
async def generate_pdf(
    request: PDFGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate both Heat Map and Investment Brief PDFs

    Args:
        request: PDF generation request with heat map data
        background_tasks: FastAPI background tasks for cleanup

    Returns:
        PDFGenerationResponse with URLs to both PDFs
    """
    try:
        # Validate heat map has exactly 30 items
        if len(request.heat_map) != 30:
            raise HTTPException(
                status_code=400,
                detail=f"Heat map must contain exactly 30 items, got {len(request.heat_map)}"
            )

        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sanitize deal name for filename
        safe_deal_name = "".join(
            c for c in request.deal_name if c.isalnum() or c in (' ', '-', '_')
        ).replace(' ', '_')

        # Generate filenames
        heat_map_filename = f"{safe_deal_name}_HeatMap_{timestamp}_{analysis_id}.pdf"
        brief_filename = f"{safe_deal_name}_InvestmentBrief_{timestamp}_{analysis_id}.pdf"

        heat_map_path = os.path.join(OUTPUT_DIR, heat_map_filename)
        brief_path = os.path.join(OUTPUT_DIR, brief_filename)

        # Generate Heat Map PDF (Grid Format)
        generate_heat_map_pdf(
            heat_map=request.heat_map,
            deal_name=request.deal_name,
            address=request.address,
            output_path=heat_map_path
        )

        # Generate Investment Brief PDF (Narrative Format)
        generate_investment_brief_pdf(
            heat_map=request.heat_map,
            deal_name=request.deal_name,
            address=request.address,
            research_data=request.research_data,
            output_path=brief_path
        )

        # Schedule cleanup of old PDFs
        background_tasks.add_task(cleanup_old_pdfs)

        # Return response with download URLs
        base_url = os.getenv("PDF_SERVICE_BASE_URL", "http://localhost:8000")

        return PDFGenerationResponse(
            status="success",
            analysis_id=analysis_id,
            deal_name=request.deal_name,
            heat_map_url=f"{base_url}/download/{heat_map_filename}",
            investment_brief_url=f"{base_url}/download/{brief_filename}",
            generated_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Download a generated PDF

    Args:
        filename: Name of the PDF file

    Returns:
        PDF file download
    """
    filepath = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=filename
    )

@app.delete("/delete/{filename}")
async def delete_pdf(filename: str):
    """
    Delete a generated PDF (for cleanup)

    Args:
        filename: Name of the PDF file

    Returns:
        Deletion confirmation
    """
    filepath = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        os.remove(filepath)
        return {"status": "success", "message": f"Deleted {filename}"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete PDF: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
