"""Expand service for multiplying rows by defects.

Implements Requirements 4.1, 4.2, 4.3, 4.4:
- Creates a separate row for each defect
- Copies all original columns
- Adds "Дефект" column with individual defect text
- Extracts photo URLs from valueString into "Фото" column
"""

import logging
import re
from typing import Optional
from app.models.schemas import ExpandedRow


logger = logging.getLogger(__name__)


DEFECT_COLUMN_NAME = "Дефект"
PHOTO_COLUMN_NAME = "Фото"

# Pattern to match domyland photo URLs
PHOTO_URL_PATTERN = re.compile(r'https://uploads\.domyland\.com/[^\s,;]+')


def extract_photo_urls(text: str) -> tuple[str, str]:
    """
    Extract photo URLs from text and return cleaned text + URLs.
    
    Args:
        text: Text that may contain photo URLs
        
    Returns:
        Tuple of (cleaned_text, photo_urls)
        - cleaned_text: Original text with URLs removed
        - photo_urls: Comma-separated list of extracted URLs
    """
    if not text:
        return "", ""
    
    # Find all photo URLs
    urls = PHOTO_URL_PATTERN.findall(text)
    
    if not urls:
        return text, ""
    
    # Remove URLs from text
    cleaned_text = PHOTO_URL_PATTERN.sub('', text)
    # Clean up extra whitespace and commas left after URL removal
    cleaned_text = re.sub(r'\s*,\s*,\s*', ', ', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip(' ,;')
    
    # Join URLs with comma
    photo_urls = ', '.join(urls)
    
    return cleaned_text, photo_urls


def expand_rows(
    rows: list[dict],
    defects_per_row: list[list[str]],
    defect_column: str = DEFECT_COLUMN_NAME,
) -> list[ExpandedRow]:
    """
    Expand rows by multiplying each row by its defects.
    
    For each input row, creates N output rows where N is the number
    of defects extracted from that row. Each output row contains
    all original columns plus a new "Дефект" column with the defect text.
    
    Args:
        rows: List of original row dictionaries from ExcelReader
        defects_per_row: List of defect lists, one per input row.
                        defects_per_row[i] contains defects for rows[i]
        defect_column: Name of the defect column to add (default: "Дефект")
        
    Returns:
        List of ExpandedRow objects, one per defect
        
    Raises:
        ValueError: If rows and defects_per_row have different lengths
        
    Example:
        >>> rows = [{"ID": "1", "valueString": "место", "valueText": "дефект"}]
        >>> defects = [["дефект 1", "дефект 2"]]
        >>> result = expand_rows(rows, defects)
        >>> len(result)  # 2 rows, one per defect
        2
    """
    if len(rows) != len(defects_per_row):
        raise ValueError(
            f"Mismatch: {len(rows)} rows but {len(defects_per_row)} defect lists"
        )
    
    expanded: list[ExpandedRow] = []
    
    for row, defects in zip(rows, defects_per_row):
        # Extract photo URLs from valueString once per row
        photo_urls = ""
        cleaned_value_string = None
        value_string_key = None
        value_text_key = None
        value_text_content = ""
        
        for key in row.keys():
            key_upper = key.upper()
            if key_upper == "VALUESTRING":
                value_string_key = key
                value_string = row.get(key, "") or ""
                cleaned_value_string, photo_urls = extract_photo_urls(value_string)
            elif key_upper == "VALUETEXT":
                value_text_key = key
                value_text_content = row.get(key, "") or ""
        
        # If no defects found but row has valueText content, use valueText as fallback defect
        # This prevents losing rows where LLM couldn't parse the defects
        if not defects:
            if value_text_content and value_text_content.strip():
                # Use original valueText as the defect (better than losing the row)
                defects = [value_text_content.strip()]
                logger.warning(f"No defects found, using valueText as fallback: '{value_text_content[:100]}...'")
            else:
                # Truly empty row - skip it
                continue
        
        # Create one expanded row per defect
        for defect_text in defects:
            # Copy all original columns
            original_data = row.copy()
            
            # Replace valueText with individual defect text (not the full original)
            # This ensures each row has only its specific defect in valueText
            for key in list(original_data.keys()):
                if key.upper() == "VALUETEXT":
                    original_data[key] = defect_text
            
            # Remove photo URLs from valueString
            if value_string_key and cleaned_value_string is not None:
                original_data[value_string_key] = cleaned_value_string
            
            # Add defect column with defect text
            original_data[defect_column] = defect_text
            
            # Add photo column with extracted URLs
            original_data[PHOTO_COLUMN_NAME] = photo_urls
            
            expanded_row = ExpandedRow(
                original_data=original_data,
                defect_text=defect_text,
                category=None,  # Will be filled by ClassifyService
            )
            expanded.append(expanded_row)
    
    return expanded


def expand_single_row(
    row: dict,
    defects: list[str],
    defect_column: str = DEFECT_COLUMN_NAME,
) -> list[ExpandedRow]:
    """
    Expand a single row by its defects.
    
    Convenience function for processing one row at a time.
    
    Args:
        row: Original row dictionary
        defects: List of defect texts for this row
        defect_column: Name of the defect column to add
        
    Returns:
        List of ExpandedRow objects, one per defect
    """
    return expand_rows([row], [defects], defect_column)
