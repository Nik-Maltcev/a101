"""Category index for fuzzy search of defect categories.

Implements Requirements 5.1, 5.2, 5.3, 6.1:
- Loads category reference from data/categories.xlsx
- Builds fuzzy index for fast search
- Finds top-N similar categories
- Tracks file changes and rebuilds index
"""

import os
from pathlib import Path
from typing import Optional

from openpyxl import load_workbook
from rapidfuzz import fuzz, process


class CategoryIndexError(Exception):
    """Base exception for CategoryIndex errors."""
    pass


class CategoryFileNotFoundError(CategoryIndexError):
    """Raised when the categories file is not found."""
    pass


class CategoryIndex:
    """Index for fast fuzzy search of defect categories.
    
    Uses rapidfuzz for efficient fuzzy string matching.
    Automatically tracks file changes and rebuilds index when needed.
    """
    
    def __init__(self, categories_path: str | Path):
        """Initialize CategoryIndex.
        
        Args:
            categories_path: Path to the categories.xlsx file
        """
        self._categories_path = Path(categories_path)
        self._categories: list[str] = []
        self._file_mtime: Optional[float] = None
        self._index_built = False
    
    @property
    def categories(self) -> list[str]:
        """Get the list of loaded categories."""
        return self._categories.copy()
    
    @property
    def is_loaded(self) -> bool:
        """Check if categories are loaded and index is built."""
        return self._index_built and len(self._categories) > 0
    
    def load_categories(self) -> list[str]:
        """Load categories from the Excel file.
        
        Reads the first column of the first sheet as category names.
        Filters out section headers (lines starting with digits like "01.", "02.").
        
        Returns:
            List of category strings
            
        Raises:
            CategoryFileNotFoundError: If file doesn't exist
            CategoryIndexError: If file cannot be read
        """
        import re
        
        if not self._categories_path.exists():
            raise CategoryFileNotFoundError(
                f"Categories file not found: {self._categories_path}"
            )
        
        try:
            workbook = load_workbook(
                filename=self._categories_path, 
                read_only=True, 
                data_only=True
            )
            sheet = workbook.active
            
            if sheet is None:
                raise CategoryIndexError("No active sheet found in categories file")

            categories = []
            # Pattern to match section headers like "01.", "02.", etc.
            section_pattern = re.compile(r'^\d+\.\s')
            
            # Read first column, skip header row
            for row in sheet.iter_rows(min_row=2, max_col=1, values_only=True):
                cell_value = row[0]
                if cell_value is not None:
                    category = str(cell_value).strip()
                    if category:
                        # Skip section headers (start with digits like "01.", "02.")
                        if section_pattern.match(category):
                            continue
                        categories.append(category)
            
            workbook.close()
            
            self._categories = categories
            self._file_mtime = os.path.getmtime(self._categories_path)
            
            return categories
            
        except CategoryIndexError:
            raise
        except Exception as e:
            raise CategoryIndexError(f"Failed to load categories: {e}")
    
    def build_index(self) -> None:
        """Build the fuzzy search index.
        
        Loads categories if not already loaded, then prepares
        the index for fast fuzzy matching.
        
        Raises:
            CategoryIndexError: If categories cannot be loaded
        """
        if not self._categories:
            self.load_categories()
        
        # rapidfuzz doesn't require explicit index building,
        # but we mark the index as ready for use
        self._index_built = True
    
    def find_top_n(self, text: str, n: int = 10) -> list[str]:
        """Find the N most similar categories for the given text.
        
        Uses fuzzy string matching to find categories that best match
        the input text.
        
        Args:
            text: The defect text to match against categories
            n: Number of top matches to return (default: 10)
            
        Returns:
            List of up to N category strings, ordered by similarity
            
        Raises:
            CategoryIndexError: If index is not built
        """
        if not self._index_built:
            raise CategoryIndexError(
                "Index not built. Call build_index() first."
            )
        
        if not self._categories:
            return []
        
        if not text or not text.strip():
            # Return first N categories for empty input
            return self._categories[:n]
        
        query = text.strip().lower()
        
        # Use token_set_ratio for better matching of partial phrases
        # It handles word order and partial matches better than WRatio
        results = process.extract(
            query=query,
            choices=self._categories,
            scorer=fuzz.token_set_ratio,
            limit=n * 2  # Get more candidates initially
        )
        
        # Also try partial_ratio for substring matches
        partial_results = process.extract(
            query=query,
            choices=self._categories,
            scorer=fuzz.partial_ratio,
            limit=n
        )
        
        # Combine and deduplicate results, prioritizing higher scores
        seen = set()
        combined = []
        
        # Merge both result sets
        all_results = list(results) + list(partial_results)
        all_results.sort(key=lambda x: x[1], reverse=True)
        
        for match, score, idx in all_results:
            if match not in seen:
                seen.add(match)
                combined.append(match)
                if len(combined) >= n:
                    break
        
        return combined
    
    def check_and_rebuild(self) -> bool:
        """Check if the categories file has changed and rebuild if needed.
        
        Compares the file modification time with the cached value.
        If the file has been modified, reloads categories and rebuilds index.
        
        Returns:
            True if index was rebuilt, False otherwise
            
        Raises:
            CategoryIndexError: If rebuild fails
        """
        if not self._categories_path.exists():
            raise CategoryFileNotFoundError(
                f"Categories file not found: {self._categories_path}"
            )
        
        current_mtime = os.path.getmtime(self._categories_path)
        
        # Rebuild if file was modified or index was never built
        if self._file_mtime is None or current_mtime > self._file_mtime:
            self.load_categories()
            self.build_index()
            return True
        
        return False
