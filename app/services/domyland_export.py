"""Service for exporting Domyland data to Excel."""

import logging
import re
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta

from openpyxl import Workbook

from app.services.domyland_client import DomylandClient

logger = logging.getLogger(__name__)

# Regex to find image URLs from domyland uploads
PHOTO_URL_PATTERN = re.compile(r'https?://uploads\.domyland\.com/[a-zA-Z0-9_-]+\.(jpeg|jpg|png|gif)', re.IGNORECASE)

# Moscow timezone (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))


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
                        # Convert to Moscow time
                        value = datetime.fromtimestamp(value, tz=MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
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
        
        Exports fields: id, address, title, valueString, valueText, extId, createdAt
        
        Field mapping:
        - valueString: answers from orderElements (dropdown/checkbox values)
        - valueText: customerSummary (contains detailed defect descriptions)
        """
        raw_data = await self.client.get_orders_with_invoices(
            building_id=building_id,
            created_at=created_at,
        )
        
        # Transform data to extract only needed fields
        data = []
        for order in raw_data:
            order_elements = order.get("orderElements", [])
            
            # Collect all values from orderElements
            value_strings = []
            for elem in order_elements:
                val_title = elem.get("valueTitle")
                if val_title:
                    val_str = str(val_title).strip()
                    if val_str:
                        value_strings.append(val_str)
            
            # Remove duplicates while preserving order
            value_strings = list(dict.fromkeys(value_strings))
            
            # customerSummary contains the detailed defect text!
            raw_value_text = order.get("customerSummary") or ""
            
            # Extract photo URLs and remove them from valueText
            photo_urls = PHOTO_URL_PATTERN.findall(raw_value_text)
            # findall returns tuples with extension, we need full URLs
            photo_urls = PHOTO_URL_PATTERN.findall(raw_value_text)
            full_photo_urls = [m.group(0) for m in PHOTO_URL_PATTERN.finditer(raw_value_text)]
            
            # Remove photo URLs from text
            value_text = PHOTO_URL_PATTERN.sub('', raw_value_text).strip()
            # Clean up extra spaces/newlines left after URL removal
            value_text = re.sub(r'\s+', ' ', value_text).strip()
            
            # Join photo URLs with newline for the Фото column
            photos = '\n'.join(full_photo_urls) if full_photo_urls else ""
            
            # Build address
            address = order.get("placeAddress") or order.get("buildingTitle") or ""
            
            # Convert timestamp
            created_at_ts = order.get("createdAt")
            created_at_str = ""
            if created_at_ts and isinstance(created_at_ts, int):
                try:
                    # Convert to Moscow time
                    created_at_str = datetime.fromtimestamp(created_at_ts, tz=MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
                except:
                    created_at_str = str(created_at_ts)
            
            row = {
                "id": order.get("id"),
                "ФИО": order.get("customerFullName") or order.get("customerShortName") or "",
                "Телефон": order.get("customerPhoneNumber") or "",
                "address": address,
                "placeNumber": order.get("placeNumber") or "",
                "placeId": order.get("placeId") or "",
                "placeExtId": order.get("placeExtId") or "",
                "title": order.get("serviceTitle") or "",
                "valueString": " | ".join(value_strings) if value_strings else "",
                "valueText": value_text,
                "Фото": photos,
                "extId": order.get("extId"),
                "createdAt": created_at_str,
            }
            data.append(row)
        
        return self._write_to_excel_ordered(data, output_path, "Orders", 
            ["id", "ФИО", "Телефон", "address", "placeNumber", "placeId", "placeExtId", "title", "valueString", "valueText", "Фото", "extId", "createdAt"])
    
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
    
    async def export_orders_raw(
        self,
        output_path: Path,
        building_id: Optional[int] = None,
        created_at: Optional[str] = None,
        limit: int = 100,  # Limit for debugging
    ) -> Path:
        """Export orders with ALL fields (raw data for debugging). Limited to first N records."""
        # Get just first page for debugging
        params = {"fromRow": 0}
        if building_id:
            params["buildingId"] = building_id
        if created_at:
            params["createdAt"] = created_at
        
        data = await self.client._request("GET", "orders", params=params)
        items = data.get("items", [])[:limit]
        
        return self._write_to_excel(items, output_path, "Orders_Raw")
    
    async def export_order_comments(
        self,
        output_path: Path,
        order_ids: list[int],
    ) -> Path:
        """Export comments for specific orders."""
        all_comments = []
        for order_id in order_ids[:50]:  # Limit to 50 orders
            comments = await self.client.get_order_comments(order_id)
            for comment in comments:
                comment["orderId"] = order_id
                all_comments.append(comment)
        return self._write_to_excel(all_comments, output_path, "Order_Comments")
    
    async def export_acceptance_results(
        self,
        output_path: Path,
        building_id: Optional[int] = None,
    ) -> Path:
        """Export acceptance results (приёмка помещений)."""
        data = await self.client.get_acceptance_results(building_id=building_id)
        return self._write_to_excel(data, output_path, "Acceptance_Results")
    
    async def export_acceptance_defects(
        self,
        output_path: Path,
        building_id: Optional[int] = None,
    ) -> Path:
        """Export acceptance defects."""
        data = await self.client.get_acceptance_defects(building_id=building_id)
        return self._write_to_excel(data, output_path, "Acceptance_Defects")
    
    async def export_columns_list(self, output_path: Path) -> Path:
        """Export available columns list for orders."""
        data = await self.client.get_orders_export_columns()
        if isinstance(data, list):
            return self._write_to_excel(data, output_path, "Export_Columns")
        elif isinstance(data, dict):
            return self._write_to_excel([data], output_path, "Export_Columns")
        return self._write_to_excel([], output_path, "Export_Columns")
