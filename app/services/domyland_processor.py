"""Service for processing Domyland export files.

This is a separate processor for files exported from Domyland API.
It uses "|" as delimiter and doesn't treat location objects (Окно, Стена) as defects.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# Known location/object keywords that should NOT be treated as defects
LOCATION_KEYWORDS = [
    "окно", "окна", "стена", "стены", "пол", "потолок", "дверь", "двери",
    "балкон", "лоджия", "санузел", "кухня", "комната", "коридор", "прихожая",
    "витраж", "витражи", "фасад", "кровля", "подъезд", "лестница",
]


def is_location_only(text: str) -> bool:
    """Check if text is just a location/object name, not a defect."""
    text_lower = text.lower().strip()
    
    # Check if it's just a location keyword
    for keyword in LOCATION_KEYWORDS:
        if text_lower == keyword:
            return True
        # Also match "Окно 1", "Стена 2" etc.
        if re.match(rf"^{keyword}\s*\d*$", text_lower):
            return True
    
    return False


def split_domyland_defects(value_string: str, delimiter: str = " | ") -> list[str]:
    """
    Split Domyland valueString into individual defects.
    
    Unlike the regular split service, this:
    1. Uses "|" as delimiter (not LLM)
    2. Filters out location-only values (Окно, Стена, etc.)
    3. Keeps only actual defect descriptions
    
    Args:
        value_string: The valueString from Domyland export (e.g. "Окно | Стеклопакет: царапины | Рама: трещины")
        delimiter: The delimiter used in valueString
        
    Returns:
        List of defect descriptions (without locations)
    """
    if not value_string:
        return []
    
    # Split by delimiter
    parts = [p.strip() for p in value_string.split(delimiter)]
    
    # Filter out empty and location-only values
    defects = []
    for part in parts:
        if not part:
            continue
        
        # Skip if it's just a location name
        if is_location_only(part):
            logger.debug(f"Skipping location: {part}")
            continue
        
        defects.append(part)
    
    logger.info(f"Split Domyland defects: {len(parts)} parts -> {len(defects)} defects")
    return defects


def process_domyland_row(row: dict) -> list[dict]:
    """
    Process a single row from Domyland export and expand into multiple rows.
    
    Each defect in valueString becomes a separate row.
    
    Args:
        row: Dict with keys: id, address, title, valueString, valueText, extId, createdAt
        
    Returns:
        List of expanded rows, each with one defect
    """
    value_string = row.get("valueString", "")
    defects = split_domyland_defects(value_string)
    
    if not defects:
        # No defects found, return original row with empty defect
        return [{**row, "Дефект": ""}]
    
    # Create one row per defect
    expanded = []
    for defect in defects:
        new_row = row.copy()
        new_row["Дефект"] = defect
        expanded.append(new_row)
    
    return expanded


def process_domyland_data(rows: list[dict]) -> list[dict]:
    """
    Process all rows from Domyland export.
    
    Args:
        rows: List of dicts from Domyland export
        
    Returns:
        Expanded list with one row per defect
    """
    all_expanded = []
    
    for row in rows:
        expanded = process_domyland_row(row)
        all_expanded.extend(expanded)
    
    logger.info(f"Processed Domyland data: {len(rows)} rows -> {len(all_expanded)} expanded rows")
    return all_expanded
