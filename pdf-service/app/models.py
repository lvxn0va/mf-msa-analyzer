"""
Pydantic models for PDF service
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class HeatMapItem(BaseModel):
    """Individual criterion in the 30-point heat map"""
    id: str = Field(..., description="Criterion ID (msa_1 through msa_16, sub_1 through sub_14)")
    metric: str = Field(..., description="The metric being evaluated")
    threshold: str = Field(..., description="Passing criteria threshold")
    value: str = Field(..., description="Actual value found")
    status: str = Field(..., pattern="^(GREEN|YELLOW|RED)$", description="Traffic light status")
    reasoning: str = Field(..., min_length=20, description="Detailed explanation")
    source: str = Field(..., description="Data source citation")
    override_applied: Optional[bool] = Field(False, description="Whether user doc override was used")
    override_document: Optional[str] = Field(None, description="Name of override document")

class PDFGenerationRequest(BaseModel):
    """Request to generate investment analysis PDFs"""
    heat_map: List[HeatMapItem] = Field(..., min_length=30, max_length=30)
    deal_name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=500)
    research_data: Optional[Dict[str, Any]] = Field(None, description="Raw research data for appendix")

class PDFGenerationResponse(BaseModel):
    """Response with URLs to generated PDFs"""
    status: str = Field("success", description="Generation status")
    analysis_id: str = Field(..., description="Unique analysis identifier")
    deal_name: str
    heat_map_url: str = Field(..., description="URL to download Heat Map PDF")
    investment_brief_url: str = Field(..., description="URL to download Investment Brief PDF")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
