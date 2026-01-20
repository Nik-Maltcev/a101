"""Service for exporting Domyland data to Excel."""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from openpyxl import Workbook

from app.services.domyland_client import DomylandClient

logger = logging.getLogger(__name__)


class DomylandExportService:
    """Service for exporting data from Domyland API to Excel files."""
    
    def __init__(self, client: DomylandClient):
        self.client = client
    
    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '_') -> dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                # Convert list to string representation
                if v and isinstance(v[0], dict):
                    # For list of dicts, take first item's relevant field
                    items.append((new_key, str(v)))
                else:
                    items.append((new_key, ", ".join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _write_to_excel(self, data: list[dict], output_path: Path, sheet_name: str = "Data") -> Path:
        """Write list of dicts to Excel file."""
        if not data:
            logger.warning("No data to export")
            # Create empty file with headers
            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name
            wb.save(output_path)
            return output_path
        
        # Flatten all records
        flat_data = [self._flatten_dict(record) for record in data]
        
        # Get all unique headers
        all_headers = set()
        for record in flat_data:
            all_headers.update(record.keys())
        headers = sorted(list(all_headers))
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        # Write headers
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Write data
        for row_idx, record in enumerate(flat_data, 2):
            for col_idx, header in enumerate(headers, 1):
                value = record.get(header, "")
                # Convert timestamps to readable dates
                if isinstance(value, int) and value > 1000000000 and value < 2000000000:
                    try:
                        value = datetime.fromtimestamp(value).strftime("%d.%m.%Y %H:%M")
                    except:
                        pass
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        wb.save(output_path)
        logger.info(f"Exported {len(data)} records to {output_path}")
        return output_path
    
    async def export_buildings(self, output_path: Path, updated_at: Optional[str] = None) -> Path:
        """Export buildings to Excel."""
        data = await self.client.get_buildings(updated_at)
        return self._write_to_excel(data, output_path, "Buildings")
    
    async def export_customers(self, output_path: Path, updated_at: Optional[str] = None) -> Path:
        """Export customers to Excel."""
        data = await self.client.get_customers(updated_at)
        return self._write_to_excel(data, output_path, "Customers")
    
    async def export_places(self, output_path: Path, updated_at: Optional[str] = None) -> Path:
        """Export places to Excel."""
        data = await self.client.get_places(updated_at)
        return self._write_to_excel(data, output_path, "Places")
    
    async def export_orders(
        self,
        output_path: Path,
        building_id: Optional[int] = None,
        created_at: Optional[str] = None,
    ) -> Path:
        """Export orders to Excel.
        
        Exports only required fields: id, address, title, valueString, valueText, extId, createdAt
        
        From orderElements:
        - valueString = valueTitle (the actual value/answer, e.g. "Стена", "Окна/витражи")
        - valueText = elementTitle (the question/field name)
        """
        raw_data = await self.client.get_orders_with_invoices(
            building_id=building_id,
            created_at=created_at,
        )
        
        # Transform data to extract only needed fields
        data = []
        for order in raw_data:
            # Extract valueString and valueText from orderElements
            # valueString = actual values (defects, locations, etc.)
            # valueText = field names/questions
            value_strings = []
            value_texts = []
            
            order_elements = order.get("orderElements", [])
            for elem in order_elements:
                val = elem.get("valueTitle")
                if val:  # Only non-null values
                    value_strings.append(str(val))
                
                elem_title = elem.get("elementTitle")
                if elem_title:
                    value_texts.append(str(elem_title))
            
            # Remove duplicates while preserving order
            value_strings = list(dict.fromkeys(value_strings))
            value_texts = list(dict.fromkeys(value_texts))
            
            # Build address from available fields
            address = order.get("placeAddress") or order.get("buildingTitle") or ""
            
            # Convert timestamp to readable date
            created_at_ts = order.get("createdAt")
            created_at_str = ""
            if created_at_ts and isinstance(created_at_ts, int):
                try:
                    created_at_str = datetime.fromtimestamp(created_at_ts).strftime("%d.%m.%Y %H:%M")
                except:
                    created_at_str = str(created_at_ts)
            
            row = {
                "id": order.get("id"),
                "address": address,
                "title": order.get("serviceTitle") or order.get("orderTypeTitle") or "",
                "valueString": " | ".join(value_strings) if value_strings else "",
                "valueText": " | ".join(value_texts) if value_texts else "",
                "extId": order.get("extId"),
                "createdAt": created_at_str,
            }
            data.append(row)
        
        return self._write_to_excel_ordered(data, output_path, "Orders", 
            ["id", "address", "title", "valueString", "valueText", "extId", "createdAt"])
    
    def _write_to_excel_ordered(
        self, 
        data: list[dict], 
        output_path: Path, 
        sheet_name: str,
        headers: list[str]
    ) -> Path:
        """Write list of dicts to Excel file with specific column order."""
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        # Write headers
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Write data
        for row_idx, record in enumerate(data, 2):
            for col_idx, header in enumerate(headers, 1):
                value = record.get(header, "")
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        wb.save(output_path)
        logger.info(f"Exported {len(data)} records to {output_path}")
        return output_path
    
    async def export_payments(
        self,
        output_path: Path,
        date_time: Optional[str] = None,
    ) -> Path:
        """Export payments to Excel."""
        data = await self.client.get_payments(date_time=date_time)
        return self._write_to_excel(data, output_path, "Payments")
