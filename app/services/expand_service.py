"""Expand service for multiplying rows by defects.

Implements Requirements 4.1, 4.2, 4.3, 4.4:
- Creates a separate row for each defect
- Copies all original columns
- Adds "Дефект" column with individual defect text
"""

from typing import Optional
from app.models.schemas import ExpandedRow


DEFECT_COLUMN_NAME = "Дефект"


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
        # If no defects, skip this row (empty comment case)
        if not defects:
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
            
            # Add defect column with defect text
            original_data[defect_column] = defect_text
            
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
