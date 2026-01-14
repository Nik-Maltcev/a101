"""Celery worker configuration and tasks."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

import redis
from celery import Celery

from app.config import settings
from app.models.schemas import JobStatus, ExpandedRow

logger = logging.getLogger(__name__)

# Create Celery application
celery_app = Celery(
    "defect_classifier",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


# Redis client for job status updates
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def update_job_status(
    job_id: str,
    status: JobStatus,
    progress: int = 0,
    output_file: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """
    Update job status in Redis.
    
    Args:
        job_id: Unique job identifier
        status: New job status
        progress: Progress percentage (0-100)
        output_file: Path to output file (when completed)
        error: Error message (when failed)
    """
    r = get_redis_client()
    updates = {
        "status": status.value,
        "progress": str(progress),
        "updated_at": datetime.utcnow().isoformat(),
    }
    if output_file is not None:
        updates["output_file"] = output_file
    if error is not None:
        updates["error"] = error
    
    r.hset(f"job:{job_id}", mapping=updates)
    logger.info(f"Job {job_id}: status={status.value}, progress={progress}%")


async def _process_job_async(job_id: str, file_path: str) -> None:
    """
    Async implementation of job processing.
    
    Steps:
    1. Read xlsx file via ExcelReader
    2. Split comments into defects via SplitService (LLM)
    3. Expand rows (one row per defect)
    4. Classify defects via ClassifyService (LLM)
    5. Write result file via ExcelWriter
    6. Update job status to completed
    
    Args:
        job_id: Unique job identifier
        file_path: Path to uploaded xlsx file
    """
    # Import services here to avoid circular imports
    from app.services.excel_reader import ExcelReader, ExcelReaderError
    from app.services.split_service import SplitService
    from app.services.expand_service import expand_rows
    from app.services.classify_service import ClassifyService
    from app.services.excel_writer import ExcelWriter, get_output_path
    from app.services.category_index import CategoryIndex
    from app.services.llm_client import LLMClient
    
    llm_client = None
    
    try:
        # Initialize services
        llm_client = LLMClient()
        category_index = CategoryIndex(settings.CATEGORIES_FILE)
        category_index.build_index()
        
        split_service = SplitService(llm_client)
        classify_service = ClassifyService(llm_client, category_index)
        excel_reader = ExcelReader()
        excel_writer = ExcelWriter()
        
        # Step 1: Read xlsx file (Requirement 2.1)
        logger.info(f"Job {job_id}: Reading file {file_path}")
        update_job_status(job_id, JobStatus.PENDING, progress=5)
        
        rows = excel_reader.read_file(file_path)
        total_rows = len(rows)
        logger.info(f"Job {job_id}: Read {total_rows} rows")
        
        if total_rows == 0:
            # No data to process
            output_path = get_output_path(job_id, settings.RESULTS_DIR)
            excel_writer.write_result([], str(output_path))
            update_job_status(
                job_id,
                JobStatus.COMPLETED,
                progress=100,
                output_file=str(output_path),
            )
            return
        
        # Extract comments by concatenating valueString + valueText
        def get_comment(row: dict) -> str:
            value_string = ""
            value_text = ""
            
            # Find valueString and valueText (case-insensitive)
            for key in row.keys():
                if key.upper() == "VALUESTRING":
                    value_string = row.get(key, "") or ""
                elif key.upper() == "VALUETEXT":
                    value_text = row.get(key, "") or ""
            
            # Concatenate with space if both exist
            if value_string and value_text:
                return f"{value_string} {value_text}"
            elif value_string:
                return value_string
            elif value_text:
                return value_text
            else:
                return ""
        
        comments = [get_comment(row) for row in rows]
        
        # Step 2: Split comments into defects (Requirement 3.1)
        logger.info(f"Job {job_id}: Splitting {len(comments)} comments")
        update_job_status(job_id, JobStatus.SPLITTING, progress=10)
        
        defects_per_row = await split_service.split_batch(comments)
        
        # Calculate total defects for progress tracking
        total_defects = sum(len(d) for d in defects_per_row)
        logger.info(f"Job {job_id}: Found {total_defects} defects")
        
        update_job_status(job_id, JobStatus.SPLITTING, progress=40)
        
        # Step 3: Expand rows (Requirement 4.1)
        logger.info(f"Job {job_id}: Expanding rows")
        expanded_rows = expand_rows(rows, defects_per_row)
        logger.info(f"Job {job_id}: Expanded to {len(expanded_rows)} rows")
        
        update_job_status(job_id, JobStatus.CLASSIFYING, progress=50)
        
        # Step 4: Classify defects (Requirement 6.1)
        if expanded_rows:
            logger.info(f"Job {job_id}: Classifying {len(expanded_rows)} defects")
            
            # Extract defect texts for classification
            defect_texts = [row.defect_text for row in expanded_rows]
            
            # Classify all defects
            categories = await classify_service.classify_batch(defect_texts)
            
            # Assign categories to expanded rows
            for i, category in enumerate(categories):
                expanded_rows[i].category = category
            
            logger.info(f"Job {job_id}: Classification complete")
        
        update_job_status(job_id, JobStatus.CLASSIFYING, progress=90)
        
        # Step 5: Write result file (Requirement 7.1)
        logger.info(f"Job {job_id}: Writing result file")
        output_path = get_output_path(job_id, settings.RESULTS_DIR)
        
        # Get original headers to preserve column order
        original_headers = list(rows[0].keys()) if rows else None
        
        excel_writer.write_result(
            expanded_rows,
            str(output_path),
            original_headers=original_headers,
        )
        
        logger.info(f"Job {job_id}: Result saved to {output_path}")
        
        # Step 6: Update status to completed (Requirement 7.4)
        update_job_status(
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            output_file=str(output_path),
        )
        
    except ExcelReaderError as e:
        logger.error(f"Job {job_id}: Excel read error - {e}")
        update_job_status(
            job_id,
            JobStatus.FAILED,
            error=f"Failed to read file: {e}",
        )
        raise
    except Exception as e:
        logger.error(f"Job {job_id}: Processing error - {e}", exc_info=True)
        update_job_status(
            job_id,
            JobStatus.FAILED,
            error=f"Processing failed: {e}",
        )
        raise
    finally:
        # Clean up LLM client
        if llm_client is not None:
            await llm_client.close()


@celery_app.task(bind=True, name="process_job")
def process_job(self, job_id: str, file_path: str):
    """
    Main task for processing uploaded Excel file.
    
    Steps:
    1. Read xlsx file
    2. Split comments into defects (LLM)
    3. Expand rows (one row per defect)
    4. Classify defects (LLM)
    5. Write result file
    
    Args:
        job_id: Unique job identifier
        file_path: Path to uploaded xlsx file
        
    Requirements: 2.1, 3.1, 4.1, 6.1, 7.1, 7.4
    """
    logger.info(f"Starting job {job_id} for file {file_path}")
    
    # Run the async processing function
    asyncio.run(_process_job_async(job_id, file_path))
