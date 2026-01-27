"""ClassifyService for classifying defects into categories.

Implements Requirements 6.1, 6.3, 6.4, 6.5, 6.6:
- Finds top-N similar categories using CategoryIndex
- Classifies defects via LLM
- Caches results for identical defects
- Supports batch processing
"""

import hashlib
import logging
from typing import Optional

from app.models.schemas import ClassifyResult
from app.services.llm_client import LLMClient
from app.services.category_index import CategoryIndex
from app.config import settings


logger = logging.getLogger(__name__)


class ClassifyServiceError(Exception):
    """Base exception for ClassifyService errors."""
    pass


class ClassifyService:
    """
    Service for classifying defects into categories using LLM.
    
    Features:
    - Uses CategoryIndex to find top-N candidate categories
    - Sends defect + candidates to LLM for final classification
    - Caches results by defect hash
    - Supports batch processing
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        category_index: CategoryIndex,
        cache: Optional[dict] = None,
        batch_size: Optional[int] = None,
        top_n: Optional[int] = None,
    ):
        """
        Initialize ClassifyService.
        
        Args:
            llm_client: LLM client for API calls
            category_index: Index for finding candidate categories
            cache: Optional cache dict (defaults to in-memory dict)
            batch_size: Batch size for processing (defaults to settings.CLASSIFY_BATCH_SIZE)
            top_n: Number of candidate categories to retrieve (defaults to settings.CATEGORY_TOP_N)
        """
        self.llm_client = llm_client
        self.category_index = category_index
        self._cache = cache if cache is not None else {}
        self.batch_size = batch_size or settings.CLASSIFY_BATCH_SIZE
        self.top_n = top_n or settings.CATEGORY_TOP_N
    
    @staticmethod
    def _compute_hash(defect: str) -> str:
        """Compute hash for a defect string."""
        return hashlib.sha256(defect.encode("utf-8")).hexdigest()
    
    def _get_from_cache(self, defect: str) -> Optional[tuple[str, int]]:
        """
        Get cached category and confidence for a defect.
        
        Args:
            defect: Defect text
            
        Returns:
            Cached tuple (category, confidence), or None if not cached
        """
        cache_key = self._compute_hash(defect)
        return self._cache.get(cache_key)
    
    def _store_in_cache(self, defect: str, category: str, confidence: int) -> None:
        """
        Store result in cache.
        
        Args:
            defect: Original defect text
            category: Assigned category
            confidence: AI confidence percentage
        """
        cache_key = self._compute_hash(defect)
        self._cache[cache_key] = (category, confidence)

    def classify_defect(self, defect: str) -> Optional[tuple[str, int]]:
        """
        Classify a single defect (sync version, cache lookup only).
        
        This method checks the cache for a previously classified defect.
        For actual LLM processing, use classify_defect_async or classify_batch.
        
        Args:
            defect: Defect text to classify
            
        Returns:
            Cached tuple (category, confidence), or None if not in cache
        """
        if not defect or not defect.strip():
            return None
        
        # Check cache
        cached = self._get_from_cache(defect)
        if cached is not None:
            logger.debug(f"Cache hit for defect hash: {self._compute_hash(defect)[:8]}")
            return cached
        
        # Return None to indicate need for LLM processing
        return None
    
    async def classify_defect_async(self, defect: str) -> tuple[str, int]:
        """
        Classify a single defect (async version with LLM call).
        
        Args:
            defect: Defect text to classify
            
        Returns:
            Tuple (category, confidence)
        """
        if not defect or not defect.strip():
            return ("НЕ ОПРЕДЕЛЕНО", 0)
        
        # Check cache
        cached = self._get_from_cache(defect)
        if cached is not None:
            logger.debug(f"Cache hit for defect hash: {self._compute_hash(defect)[:8]}")
            return cached
        
        # Process via batch (single item)
        results = await self.classify_batch([defect])
        return results[0] if results else ("НЕ ОПРЕДЕЛЕНО", 0)
    
    async def classify_batch(self, defects: list[str]) -> list[tuple[str, int]]:
        """
        Classify multiple defects using batch processing.
        
        Handles caching and batches LLM calls according to batch_size.
        
        Args:
            defects: List of defect texts to classify
            
        Returns:
            List of tuples (category, confidence), one per input defect
        """
        if not defects:
            return []
        
        results: list[Optional[tuple[str, int]]] = [None] * len(defects)
        defects_to_process: list[tuple[int, str]] = []
        
        # First pass: handle empty defects and cache hits
        for i, defect in enumerate(defects):
            # Handle empty defects
            if not defect or not defect.strip():
                results[i] = ("НЕ ОПРЕДЕЛЕНО", 0)
                continue
            
            # Check cache
            cached = self._get_from_cache(defect)
            if cached is not None:
                results[i] = cached
                logger.debug(f"Cache hit for defect {i}")
                continue
            
            # Need LLM processing
            defects_to_process.append((i, defect))
        
        # Process remaining defects via LLM
        if defects_to_process:
            logger.info(f"Processing {len(defects_to_process)} defects via LLM")
            
            # Get top-N candidate categories for each defect using rapidfuzz
            defects_with_candidates: list[dict] = []
            for idx, (original_idx, defect) in enumerate(defects_to_process):
                # Find top-N most similar categories
                candidates = self.category_index.find_top_n(defect, n=self.top_n)
                
                # Add "НЕ ОПРЕДЕЛЕНО" as fallback option
                if "НЕ ОПРЕДЕЛЕНО" not in candidates:
                    candidates.append("НЕ ОПРЕДЕЛЕНО")
                
                defects_with_candidates.append({
                    "defect": defect,
                    "candidates": candidates,
                })
                
                # Log candidates for first few defects for debugging
                if idx < 3:
                    logger.info(f"Defect {original_idx}: '{defect[:60]}...' -> top 5 candidates: {candidates[:5]}")
            
            logger.info(f"Found top-{self.top_n} candidates for each defect using rapidfuzz")
            
            # Call LLM (it handles batching internally)
            llm_results = await self.llm_client.classify_defects(defects_with_candidates)
            
            # Map results back and cache them
            all_categories = self.category_index.categories
            
            # List of invalid responses that LLM might return
            invalid_responses = {
                'другое', 'прочее', 'иное', 'не подходит', 'нет категории',
                'не найдено', 'отсутствует', 'none', 'other', ''
            }
            
            for i, (original_idx, defect) in enumerate(defects_to_process):
                if i < len(llm_results):
                    classify_result = llm_results[i]
                    category = classify_result.chosen
                    confidence = classify_result.confidence
                    
                    # Get candidates for this defect
                    candidates = defects_with_candidates[i]["candidates"]
                    
                    # Check if LLM returned invalid/invented category
                    category_lower = category.lower().strip() if category else ''
                    is_invalid = (
                        category_lower in invalid_responses or
                        category not in candidates
                    )
                    
                    if is_invalid:
                        logger.warning(
                            f"LLM returned invalid category '{category}' for defect {original_idx}. "
                            f"Selecting best match from candidates."
                        )
                        # Find closest match from candidates using fuzzy matching
                        from rapidfuzz import process as rfprocess, fuzz as rffuzz
                        
                        # Filter out "НЕ ОПРЕДЕЛЕНО" from candidates for matching
                        valid_candidates = [c for c in candidates if c != "НЕ ОПРЕДЕЛЕНО"]
                        
                        if valid_candidates:
                            best_match = rfprocess.extractOne(
                                defect,
                                valid_candidates,
                                scorer=rffuzz.token_set_ratio
                            )
                            if best_match and best_match[1] > 30:
                                category = best_match[0]
                                confidence = min(best_match[1], 50)  # Lower confidence for fallback
                                logger.info(f"Selected closest match: '{category}' (score: {best_match[1]})")
                            else:
                                # Try WRatio as fallback
                                best_match = rfprocess.extractOne(
                                    defect,
                                    valid_candidates,
                                    scorer=rffuzz.WRatio
                                )
                                if best_match and best_match[1] > 30:
                                    category = best_match[0]
                                    confidence = min(best_match[1], 40)  # Even lower confidence
                                    logger.info(f"Selected WRatio match: '{category}' (score: {best_match[1]})")
                                else:
                                    # Use first candidate as last resort
                                    category = valid_candidates[0]
                                    confidence = 20  # Very low confidence
                                    logger.warning(f"Using first candidate as fallback: '{category}'")
                        else:
                            category = "НЕ ОПРЕДЕЛЕНО"
                            confidence = 0
                            logger.warning(f"No valid candidates for defect {original_idx}")
                else:
                    # Fallback if LLM returned fewer results
                    category = "НЕ ОПРЕДЕЛЕНО"
                    confidence = 0
                    logger.warning(f"No LLM result for defect {original_idx}")
                
                results[original_idx] = (category, confidence)
                self._store_in_cache(defect, category, confidence)
        
        return results
    
    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        logger.info("ClassifyService cache cleared")
    
    @property
    def cache_size(self) -> int:
        """Return the number of cached entries."""
        return len(self._cache)
