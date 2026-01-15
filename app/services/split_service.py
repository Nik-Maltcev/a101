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
    def _clean_defect_text(text: str) -> str:
        """
        Clean defect text by removing leading numbering and whitespace.

        Handles:
        - "1. Text", "1) Text", "1 Text"
        - "1Text" (if Text starts with uppercase)
        - "- Text", "* Text"
        """
        if not text:
            return ""

        cleaned = text.strip()

        # Pattern explanation:
        # ^(\d{1,3}([\.\)]\s*|\s+|(?=[A-ZА-ЯЁ])))
        # \d{1,3} : 1 to 3 digits (avoid stripping large numbers like 2024)
        # ( ... ) : Group defining what follows
        #   [\.\)]\s* : Dot or paren, then optional space (e.g., "1.", "1) ")
        #   | : OR
        #   \s+ : At least one space (e.g., "1 Text")
        #   | : OR
        #   (?=[A-ZА-ЯЁ]) : Lookahead for uppercase letter (e.g., "1Text")

        # Also handle bullets: ^[\-\*]\s+

        # Only strip number prefix if remaining text is long enough (>5 chars)
        # This prevents stripping "5шт" -> "шт"
        
        # First try explicit separators (always strip)
        if re.match(r'^\d{1,3}[\.\)]\s*', cleaned):
            cleaned = re.sub(r'^\d{1,3}[\.\)]\s*', '', cleaned)
        elif re.match(r'^\d{1,3}\s+', cleaned):
            cleaned = re.sub(r'^\d{1,3}\s+', '', cleaned)
        # For "1Text" pattern (no separator), only strip if result is long enough
        elif re.match(r'^\d{1,3}(?=[A-ZА-ЯЁа-яё])', cleaned):
            potential_result = re.sub(r'^\d{1,3}', '', cleaned)
            if len(potential_result) > 5:  # Only strip if remaining text is substantial
                cleaned = potential_result

        # Bullet pattern
        cleaned = re.sub(r'^[\-\*]\s+', '', cleaned)

        return cleaned.strip()

    @staticmethod
    def _local_split_by_numbers(text: str) -> list[str]:
        """
        Fallback: split text by numbered lines locally without LLM.
        
        Handles multiline text where each line starts with a number.
        """
        if not text:
            return []
        
        lines = text.strip().split('\n')
        defects = []
        current_defect = []
        
        # Pattern to detect numbered lines: starts with digit(s) followed by text
        number_pattern = re.compile(r'^(\d{1,2})([\.\)\s]|(?=[А-ЯЁа-яёA-Za-z]))')
        
        # Check if this looks like a header (e.g., "Окно 2", "Кухня")
        header_pattern = re.compile(r'^(Окно|Кухня|Комната|Балкон|Лоджия|Санузел|Ванная|Коридор|Прихожая)\s*\d*', re.IGNORECASE)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip headers
            if header_pattern.match(line) and len(line) < 50:
                continue
            
            # Check if line starts with a number
            if number_pattern.match(line):
                # Save previous defect if exists
                if current_defect:
                    defect_text = ' '.join(current_defect)
                    cleaned = SplitService._clean_defect_text(defect_text)
                    if cleaned:
                        defects.append(cleaned)
                    current_defect = []
                
                # Start new defect
                current_defect.append(line)
            else:
                # Continue current defect or start new one
                if current_defect:
                    current_defect.append(line)
                else:
                    # Non-numbered line without context - treat as single defect
                    cleaned = SplitService._clean_defect_text(line)
                    if cleaned:
                        defects.append(cleaned)
        
        # Don't forget the last defect
        if current_defect:
            defect_text = ' '.join(current_defect)
            cleaned = SplitService._clean_defect_text(defect_text)
            if cleaned:
                defects.append(cleaned)
        
        return defects

    def _validate_split_result(self, comment: str, defects: list[str]) -> list[str]:
        """
        Validate split result and apply fallback if needed.
        
        Checks for:
        - All defects being identical (LLM error)
        - Defects being just numbers
        - Empty results when input has numbered lines
        """
        if not defects:
            # Check if input has numbered lines - try local split
            if re.search(r'\n\s*\d{1,2}[\.\)\s]', comment) or re.search(r'\n\s*\d{1,2}[А-ЯЁа-яё]', comment):
                logger.warning("LLM returned empty but input has numbered lines, trying local split")
                return self._local_split_by_numbers(comment)
            return defects
        
        # Check if all defects are identical
        unique_defects = set(defects)
        if len(unique_defects) == 1 and len(defects) > 1:
            logger.warning(f"All {len(defects)} defects are identical: '{defects[0][:50]}...', trying local split")
            local_result = self._local_split_by_numbers(comment)
            if local_result and len(set(local_result)) > 1:
                return local_result
        
        # Check if defects are just numbers or very short
        valid_defects = [d for d in defects if len(d) > 3 and not d.isdigit()]
        if len(valid_defects) < len(defects):
            logger.warning(f"Filtered out {len(defects) - len(valid_defects)} invalid defects (too short or just numbers)")
            return valid_defects
        
        return defects

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
                    defect_texts = [self._clean_defect_text(d.text) for d in split_result.defects]
                    
                    # Validate and potentially fix the result
                    defect_texts = self._validate_split_result(comment, defect_texts)
                else:
                    # Fallback if LLM returned fewer results
                    defect_texts = self._local_split_by_numbers(comment)
                    logger.warning(f"No LLM result for comment {original_idx}, used local split: {len(defect_texts)} defects")
                
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
