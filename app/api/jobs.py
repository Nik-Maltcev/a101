"""API endpoints for job management."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict

import redis
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.models import Job, JobResponse, JobStatus, JobStatusResponse
from app.worker.tasks import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Redis client for job storage
_redis_client = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def get_job(job_id: str) -> Job | None:
    """Get job from Redis storage."""
    r = get_redis_client()
    job_data = r.hgetall(f"job:{job_id}")
    if not job_data:
        return None
    return Job(
        id=job_data["id"],
        status=JobStatus(job_data["status"]),
        progress=int(job_data["progress"]),
        input_file=job_data["input_file"],
        output_file=job_data.get("output_file") or None,
        error=job_data.get("error") or None,
        created_at=datetime.fromisoformat(job_data["created_at"]),
        updated_at=datetime.fromisoformat(job_data["updated_at"]),
    )


def save_job(job: Job) -> None:
    """Save job to Redis storage."""
    r = get_redis_client()
    job_data = {
        "id": job.id,
        "status": job.status.value,
        "progress": str(job.progress),
        "input_file": job.input_file,
        "output_file": job.output_file or "",
        "error": job.error or "",
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }
    r.hset(f"job:{job.id}", mapping=job_data)
    # Set expiration to 24 hours
    r.expire(f"job:{job.id}", 86400)


@router.post("", response_model=JobResponse)
async def create_job(file: UploadFile = File(...)) -> JobResponse:
    """
    Upload an Excel file for processing.
    
    Accepts only .xlsx files. Creates a job in the queue and returns job_id.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    # Validate file format (Requirement 1.1)
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are accepted"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds limit of {settings.MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # Generate unique job_id (Requirement 1.2)
    job_id = str(uuid.uuid4())
    
    # Save file to uploads/ (Requirement 1.3)
    file_path = settings.UPLOADS_DIR / f"{job_id}.xlsx"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create job record
    now = datetime.utcnow()
    job = Job(
        id=job_id,
        status=JobStatus.PENDING,
        progress=0,
        input_file=str(file_path),
        output_file=None,
        error=None,
        created_at=now,
        updated_at=now,
    )
    save_job(job)
    
    # Create task in queue (Requirement 1.5)
    process_job.delay(job_id, str(file_path))
    
    return JobResponse(job_id=job_id)


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the status of a processing job.
    
    Returns status, progress percentage, and download URL when completed.
    
    Requirements: 8.1, 8.2
    """
    job = get_job(job_id)
    
    # Job not found (Requirement 8.4)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Build download URL if completed (Requirement 8.2)
    download_url = None
    if job.status == JobStatus.COMPLETED and job.output_file:
        download_url = f"/jobs/{job_id}/download"
    
    return JobStatusResponse(
        status=job.status,
        progress=job.progress,
        download_url=download_url,
        error=job.error,
    )


@router.get("/{job_id}/download")
async def download_result(job_id: str) -> FileResponse:
    """
    Download the processed result file.
    
    Only available when job status is 'completed'.
    
    Requirements: 8.3, 8.4
    """
    job = get_job(job_id)
    
    # Job not found
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Job not completed yet
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not completed yet")
    
    # Check output file exists
    if not job.output_file:
        raise HTTPException(status_code=404, detail="Result file not found")
    
    output_path = Path(job.output_file)
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    # Return file (Requirement 8.3)
    return FileResponse(
        path=str(output_path),
        filename=f"{job_id}_processed.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
