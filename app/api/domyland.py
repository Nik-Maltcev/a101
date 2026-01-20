"""API endpoints for Domyland integration."""

import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings
from app.services.domyland_client import DomylandClient, DomylandAuthError, DomylandClientError
from app.services.domyland_export import DomylandExportService

router = APIRouter(prefix="/domyland", tags=["domyland"])


# Store tokens in memory (in production use Redis/DB)
_tokens: dict[str, dict] = {}


class AuthRequest(BaseModel):
    """Authentication request."""
    email: str
    password: str
    tenant_name: str = "a101"


class AuthResponse(BaseModel):
    """Authentication response."""
    success: bool
    message: str
    session_id: Optional[str] = None
    available_exports: Optional[list[dict]] = None  # List of available export types


class ExportRequest(BaseModel):
    """Export request."""
    session_id: str
    export_type: str  # buildings, customers, places, orders, payments
    # Optional filters
    building_id: Optional[int] = None
    created_at: Optional[str] = None  # DD.MM.YYYY-DD.MM.YYYY
    updated_at: Optional[str] = None


class ExportResponse(BaseModel):
    """Export response."""
    success: bool
    message: str
    download_url: Optional[str] = None
    record_count: Optional[int] = None


@router.post("/auth", response_model=AuthResponse)
async def authenticate(request: AuthRequest) -> AuthResponse:
    """
    Authenticate with Domyland API.
    
    Returns a session_id to use for subsequent requests.
    Also checks which export types are available for this user.
    """
    client = DomylandClient()
    
    try:
        token = await client.authenticate(
            email=request.email,
            password=request.password,
            tenant_name=request.tenant_name,
        )
        
        # Check available permissions
        available_exports = await _check_permissions(client)
        
        # Generate session ID and store token
        session_id = str(uuid.uuid4())
        _tokens[session_id] = {
            "token": token,
            "tenant_name": request.tenant_name,
            "created_at": datetime.utcnow().isoformat(),
            "available_exports": [e["id"] for e in available_exports],
        }
        
        return AuthResponse(
            success=True,
            message=f"Авторизация успешна. Доступно {len(available_exports)} типов экспорта.",
            session_id=session_id,
            available_exports=available_exports,
        )
        
    except DomylandAuthError as e:
        return AuthResponse(
            success=False,
            message=str(e),
        )
    finally:
        await client.close()


async def _check_permissions(client: DomylandClient) -> list[dict]:
    """Check which API endpoints are accessible for the authenticated user."""
    all_types = [
        {"id": "buildings", "name": "Объекты/здания", "endpoint": "buildings"},
        {"id": "places", "name": "Помещения", "endpoint": "places"},
        {"id": "orders", "name": "Заявки со счетами", "endpoint": "orders/invoices"},
        {"id": "customers", "name": "Клиенты", "endpoint": "customers"},
        {"id": "payments", "name": "Платежи", "endpoint": "payments"},
    ]
    
    available = []
    for export_type in all_types:
        try:
            # Try to fetch first page to check access
            await client._request("GET", export_type["endpoint"], params={"fromRow": 0})
            available.append({
                "id": export_type["id"],
                "name": export_type["name"],
            })
        except DomylandClientError:
            # No access to this endpoint
            pass
    
    return available


@router.post("/export", response_model=ExportResponse)
async def export_data(request: ExportRequest) -> ExportResponse:
    """
    Export data from Domyland to Excel file.
    
    Supported export_type values:
    - buildings: Объекты/здания
    - customers: Клиенты
    - places: Помещения
    - orders: Заявки со счетами
    - payments: Платежи
    """
    # Check session
    session = _tokens.get(request.session_id)
    if not session:
        return ExportResponse(
            success=False,
            message="Сессия не найдена. Авторизуйтесь заново.",
        )
    
    # Create client with stored token
    client = DomylandClient()
    client.set_token(session["token"])
    export_service = DomylandExportService(client)
    
    # Generate output filename
    file_id = str(uuid.uuid4())
    output_path = settings.RESULTS_DIR / f"domyland_{request.export_type}_{file_id}.xlsx"
    
    try:
        if request.export_type == "buildings":
            await export_service.export_buildings(output_path, request.updated_at)
        elif request.export_type == "customers":
            await export_service.export_customers(output_path, request.updated_at)
        elif request.export_type == "places":
            await export_service.export_places(output_path, request.updated_at)
        elif request.export_type == "orders":
            await export_service.export_orders(
                output_path,
                building_id=request.building_id,
                created_at=request.created_at,
            )
        elif request.export_type == "payments":
            await export_service.export_payments(output_path, request.created_at)
        else:
            return ExportResponse(
                success=False,
                message=f"Неизвестный тип экспорта: {request.export_type}",
            )
        
        # Count records in file
        from openpyxl import load_workbook
        wb = load_workbook(output_path, read_only=True)
        record_count = wb.active.max_row - 1  # Minus header
        wb.close()
        
        return ExportResponse(
            success=True,
            message=f"Экспорт завершён: {record_count} записей",
            download_url=f"/domyland/download/{file_id}?type={request.export_type}",
            record_count=record_count,
        )
        
    except DomylandAuthError:
        # Token expired, remove session
        _tokens.pop(request.session_id, None)
        return ExportResponse(
            success=False,
            message="Сессия истекла. Авторизуйтесь заново.",
        )
    except DomylandClientError as e:
        return ExportResponse(
            success=False,
            message=f"Ошибка API: {e}",
        )
    except Exception as e:
        return ExportResponse(
            success=False,
            message=f"Ошибка экспорта: {e}",
        )
    finally:
        await client.close()


@router.get("/download/{file_id}")
async def download_export(
    file_id: str,
    type: str = Query(..., description="Export type"),
) -> FileResponse:
    """Download exported Excel file."""
    output_path = settings.RESULTS_DIR / f"domyland_{type}_{file_id}.xlsx"
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(
        path=str(output_path),
        filename=f"domyland_{type}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/export-types")
async def get_export_types():
    """Get available export types."""
    return {
        "types": [
            {"id": "buildings", "name": "Объекты/здания", "description": "Список зданий и объектов"},
            {"id": "customers", "name": "Клиенты", "description": "Список клиентов"},
            {"id": "places", "name": "Помещения", "description": "Список помещений/квартир"},
            {"id": "orders", "name": "Заявки со счетами", "description": "Заявки с информацией об оплате"},
            {"id": "payments", "name": "Платежи", "description": "История платежей"},
        ]
    }
