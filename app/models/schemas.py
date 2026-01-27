"""Pydantic schemas for the Defect Classifier service."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class JobStatus(str, Enum):
    """Status of a processing job."""
    PENDING = "pending"
    SPLITTING = "splitting"
    CLASSIFYING = "classifying"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Internal job representation."""
    id: str
    status: JobStatus
    progress: int  # 0-100
    input_file: str
    output_file: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JobResponse(BaseModel):
    """Response returned when creating a new job."""
    job_id: str


class JobStatusResponse(BaseModel):
    """Response for job status queries."""
    status: JobStatus
    progress: int
    download_url: Optional[str] = None
    error: Optional[str] = None


class DefectItem(BaseModel):
    """Single defect item from split result."""
    text: str


class SplitResult(BaseModel):
    """Result of splitting a comment into defects."""
    defects: list[DefectItem]


class ClassifyResult(BaseModel):
    """Result of classifying a defect."""
    chosen: str  # category name
    confidence: int = 0  # confidence percentage 0-100


class ExpandedRow(BaseModel):
    """Row after expansion - one row per defect."""
    original_data: dict  # all original columns
    defect_text: str
    category: Optional[str] = None
    confidence: Optional[int] = None  # AI confidence percentage
