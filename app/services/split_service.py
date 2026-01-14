"""SplitService for splitting comments into individual defects."""

import hashlib
import logging
import re
from typing import Optional

from app.models.schemas import SplitResult, DefectItem
from app.services.llm_client import LLMClient
from app.config import settings


logger = logging.getLogger(__name__)


class SplitServiceError(Exception):
    """Base exception for SplitService errors."""
    pass


class SplitService:
    """
    Service for splitting comments into individual defects using LLM.
    
    Features:
    - Handles empty comments and "нет замечаний" cases
    - Caches results by comment hash
    - Supports batch processing
    """
    
    # Patterns that indicate no defects
    NO_DEFECTS_PATTERNS = [
        r"^\s*$",  # Empty or whitespace only
        r"нет\s+замечаний",  # "нет замечаний"
        r"без\s+замечаний",  # "без замечаний"
        r"замечания\s+отсутствуют",  # "замечания отсутствуют"
    ]
    
    def __init__(
        self,
        llm_client: LLMClient,
        cache: Optional[dict] = None,
        batch_size: Optional[int] = None,
    ):
        """
        Initialize SplitService.
        
        Args:
            llm_client: LLM client for API calls
            cache: Optional cache dict (defaults to in-memory dict)
            batch_size: Batch size for processing (defaults to settings.SPLIT_BATCH_SIZE)
        """
        self.llm_client = llm_client
        self._cache = cache if cache is not None else {}
        self.batch_size = batch_size or settings.SPLIT_BATCH_SIZE
        
        # Compile patterns for efficiency (case-insensitive)
        self._no_defects_regex = re.compile(
            "|".join(self.NO_DEFECTS_PATTERNS),
            re.IGNORECASE
        )
    
    @staticmethod
    def _compute_hash(comment: str) -> str:
        """Compute hash for a comment string."""
        return hashlib.sha256(comment.encode("utf-8")).hexdigest()
    
    @staticmethod
    def _split_by_numbers(text: str) -> list[str]:
        """
        Split text by numbered items (1, 2, 3... or 1., 2., 3...).
        
        Args:
            text: Text with numbered defects
            
        Returns:
            List of defect texts with numbers removed
        """
        # Pattern: digit(s) followed by optional dot/space at start or after space
        # Examples: "1Царапины", "1. Царапины", " 2Трещина"
        pattern = r'(?:^|\s)(\d+)\.?\s*'
        
        # Split by pattern and keep the parts
        parts = re.split(pattern, text)
        
        defects = []
        # parts will be like: ['', '1', 'Царапины', '2', 'Трещина', ...]
        # We want to pair numbers with following text
        i = 1  # Skip first empty element
        while i < len(parts) - 1:
            number = parts[i]
            defect_text = parts[i + 1].strip()
            if defect_text:
                defects.append(defect_text)
            i += 2
        
        # If we got defects, return them
        if defects:
            return defects
        
        # Fallback: try simpler pattern for "1Text 2Text"
        pattern2 = r'(\d+)([^\d]+?)(?=\d+|$)'
        matches = re.findall(pattern2, text)
        if matches:
            return [match[1].strip() for match in matches if match[1].strip()]
        
        # No numbered items found, return original text
        return [text]
    
    def _is_empty_comment(self, comment: str) -> bool:
        """
        Check if comment should be treated as empty (no defects).
        
        Args:
            comment: Comment text to check
            
        Returns:
            True if comment is empty or indicates no defects
        """
        if not comment:
            return True
        return bool(self._no_defects_regex.search(comment))
    
    def _get_from_cache(self, comment: str) -> Optional[list[str]]:
        """
        Get cached result for a comment.
        
        Args:
            comment: Comment text
            
        Returns:
            Cached list of defect texts, or None if not cached
        """
        cache_key = self._compute_hash(comment)
        return self._cache.get(cache_key)
    
    def _store_in_cache(self, comment: str, defects: list[str]) -> None:
        """
        Store result in cache.
        
        Args:
            comment: Original comment text
            defects: List of defect texts
        """
        cache_key = self._compute_hash(comment)
        self._cache[cache_key] = defects

    def split_comment(self, comment: str) -> list[str]:
        """
        Split a single comment into individual defects.
        
        This is a synchronous wrapper that checks cache and handles
        empty comments. For actual LLM processing, use split_batch.
        
        Args:
            comment: Comment text to split
            
        Returns:
            List of defect text strings
        """
        # Handle empty comments
        if self._is_empty_comment(comment):
            return []
        
        # Check cache
        cached = self._get_from_cache(comment)
        if cached is not None:
            logger.debug(f"Cache hit for comment hash: {self._compute_hash(comment)[:8]}")
            return cached
        
        # For single comments, we can't call LLM synchronously
        # This method is mainly for cache lookup and empty handling
        # Actual LLM calls should go through split_batch
        return None  # Indicates need for LLM processing
    
    async def split_comment_async(self, comment: str) -> list[str]:
        """
        Split a single comment into individual defects (async version).
        
        Args:
            comment: Comment text to split
            
        Returns:
            List of defect text strings
        """
        # Handle empty comments
        if self._is_empty_comment(comment):
            return []
        
        # Check cache
        cached = self._get_from_cache(comment)
        if cached is not None:
            logger.debug(f"Cache hit for comment hash: {self._compute_hash(comment)[:8]}")
            return cached
        
        # Process via LLM
        results = await self.split_batch([comment])
        return results[0] if results else []
    
    async def split_batch(self, comments: list[str]) -> list[list[str]]:
        """
        Split multiple comments into defects using batch processing.
        
        Handles caching, empty comments, and batches LLM calls.
        
        Args:
            comments: List of comment texts to split
            
        Returns:
            List of lists, where each inner list contains defect texts
            for the corresponding input comment
        """
        if not comments:
            return []
        
        results: list[list[str]] = [None] * len(comments)
        comments_to_process: list[tuple[int, str]] = []
        
        # First pass: handle empty comments and cache hits
        for i, comment in enumerate(comments):
            # Handle empty comments
            if self._is_empty_comment(comment):
                results[i] = []
                continue
            
            # Check cache
            cached = self._get_from_cache(comment)
            if cached is not None:
                results[i] = cached
                logger.debug(f"Cache hit for comment {i}")
                continue
            
            # Need LLM processing
            comments_to_process.append((i, comment))
        
        # Process remaining comments via LLM in batches
        if comments_to_process:
            logger.info(f"Processing {len(comments_to_process)} comments via LLM")
            
            # Extract just the comment texts for LLM
            indices = [idx for idx, _ in comments_to_process]
            texts = [text for _, text in comments_to_process]
            
            # Call LLM (it handles batching internally)
            logger.info(f"Calling LLM split_comments with {len(texts)} texts")
            llm_results = await self.llm_client.split_comments(texts)
            logger.info(f"LLM returned {len(llm_results)} results")
            
            # Map results back and cache them
            for i, (original_idx, comment) in enumerate(comments_to_process):
                if i < len(llm_results):
                    split_result = llm_results[i]
                    defect_texts = [d.text for d in split_result.defects]
                    
                    # Fallback: if LLM returned 1 defect but text has numbers, split programmatically
                    if len(defect_texts) == 1:
                        # Check if the single defect contains numbered items
                        if re.search(r'\d+[^\d]{10,}', defect_texts[0]):  # Has digit followed by 10+ non-digits
                            logger.info(f"Comment {original_idx}: LLM returned 1 defect but text has numbers, splitting programmatically")
                            programmatic_split = self._split_by_numbers(defect_texts[0])
                            if len(programmatic_split) > 1:
                                defect_texts = programmatic_split
                                logger.info(f"Programmatic split produced {len(defect_texts)} defects")
                else:
                    # Fallback if LLM returned fewer results
                    defect_texts = []
                    logger.warning(f"No LLM result for comment {original_idx}")
                
                results[original_idx] = defect_texts
                self._store_in_cache(comment, defect_texts)
        
        return results
    
    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        logger.info("SplitService cache cleared")
    
    @property
    def cache_size(self) -> int:
        """Return the number of cached entries."""
        return len(self._cache)
