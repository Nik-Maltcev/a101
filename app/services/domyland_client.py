"""Domyland API client for fetching data from CRM."""

import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class DomylandClientError(Exception):
    """Base exception for Domyland client errors."""
    pass


class DomylandAuthError(DomylandClientError):
    """Authentication error."""
    pass


class DomylandClient:
    """Client for Domyland CRM API.
    
    API docs: https://public-api.domyland.ru/
    """
    
    def __init__(
        self,
        base_url: str = "https://a101.domyland.ru/api",
        app_name: str = "defect-classifier",
        timezone: str = "Europe/Moscow",
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.app_name = app_name
        self.timezone = timezone
        self.timeout = timeout
        self._token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "AppName": self.app_name,
                    "TimeZone": self.timezone,
                    "Content-Type": "application/json",
                },
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def authenticate(self, email: str, password: str, tenant_name: str) -> str:
        """
        Authenticate and get token.
        
        Args:
            email: User email
            password: User password
            tenant_name: Tenant code (e.g. "a101")
            
        Returns:
            Authentication token
        """
        client = await self._get_client()
        
        try:
            response = await client.post(
                f"{self.base_url}/auth",
                json={
                    "email": email,
                    "password": password,
                    "tenantName": tenant_name,
                },
            )
            
            if response.status_code == 400:
                data = response.json()
                msg = data.get("userMessages", ["Неверный email или пароль"])[0]
                raise DomylandAuthError(msg)
            
            response.raise_for_status()
            data = response.json()
            self._token = data["token"]
            logger.info("Successfully authenticated with Domyland API")
            return self._token
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Auth failed: {e.response.status_code}")
            raise DomylandAuthError(f"Authentication failed: {e}")
        except Exception as e:
            logger.error(f"Auth error: {e}")
            raise DomylandAuthError(f"Authentication error: {e}")
    
    def set_token(self, token: str):
        """Set authentication token directly."""
        self._token = token
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict:
        """Make authenticated API request."""
        if not self._token:
            raise DomylandClientError("Not authenticated. Call authenticate() first.")
        
        client = await self._get_client()
        
        headers = {"Authorization": self._token}
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
            )
            
            if response.status_code == 401:
                raise DomylandAuthError("Token expired. Re-authenticate.")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text[:200]}")
            raise DomylandClientError(f"API error: {e.response.status_code}")
    
    async def get_all_pages(
        self, 
        endpoint: str, 
        params: Optional[dict] = None,
        max_pages: int = 1000,  # Increased for large datasets
    ) -> list[dict]:
        """
        Fetch all pages of data from paginated endpoint.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            max_pages: Maximum pages to fetch (safety limit)
            
        Returns:
            List of all items from all pages
        """
        all_items = []
        params = params or {}
        params["fromRow"] = 0
        
        for page in range(max_pages):
            logger.info(f"Fetching {endpoint} page {page + 1}, fromRow={params['fromRow']}")
            
            data = await self._request("GET", endpoint, params=params)
            
            items = data.get("items", [])
            all_items.extend(items)
            
            next_row = data.get("nextRow", -1)
            if next_row == -1:
                logger.info(f"Finished fetching {endpoint}: {len(all_items)} total items")
                break
            
            params["fromRow"] = next_row
        
        return all_items

    
    # === Export methods ===
    
    async def get_buildings(self, updated_at: Optional[str] = None) -> list[dict]:
        """Get list of buildings/objects."""
        params = {}
        if updated_at:
            params["updatedAt"] = updated_at
        return await self.get_all_pages("buildings", params)
    
    async def get_customers(self, updated_at: Optional[str] = None) -> list[dict]:
        """Get list of customers."""
        params = {}
        if updated_at:
            params["updatedAt"] = updated_at
        return await self.get_all_pages("customers", params)
    
    async def get_places(self, updated_at: Optional[str] = None) -> list[dict]:
        """Get list of places/apartments."""
        params = {}
        if updated_at:
            params["updatedAt"] = updated_at
        return await self.get_all_pages("places", params)
    
    async def get_orders_with_invoices(
        self,
        building_id: Optional[int] = None,
        place_id: Optional[int] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        order_status_id: Optional[int] = None,
        service_id: Optional[int] = None,
    ) -> list[dict]:
        """
        Get orders (regular orders endpoint, not invoices).
        
        Args:
            building_id: Filter by building
            place_id: Filter by place
            created_at: Date range (DD.MM.YYYY-DD.MM.YYYY)
            updated_at: Date range
            order_status_id: Filter by status
            service_id: Filter by service
        """
        params = {}
        if building_id:
            params["buildingId"] = building_id
        if place_id:
            params["placeId"] = place_id
        if created_at:
            params["createdAt"] = created_at
        if updated_at:
            params["updatedAt"] = updated_at
        if order_status_id:
            params["orderStatusId"] = order_status_id
        if service_id:
            params["serviceId"] = service_id
        
        # Use /orders endpoint (not /orders/invoices which may be empty)
        return await self.get_all_pages("orders", params)
    
    async def get_payments(
        self,
        date_time: Optional[str] = None,
        company_ext_id: Optional[str] = None,
    ) -> list[dict]:
        """Get payments."""
        params = {}
        if date_time:
            params["dateTime"] = date_time
        if company_ext_id:
            params["companyExtId"] = company_ext_id
        return await self.get_all_pages("payments", params)
    
    async def get_metering_data(
        self,
        building_id: Optional[int] = None,
        place_id: Optional[int] = None,
        is_last: bool = True,
    ) -> list[dict]:
        """Get metering data (individual meters)."""
        params = {"isLast": 1 if is_last else 0}
        if building_id:
            params["buildingId"] = building_id
        if place_id:
            params["placeId"] = place_id
        return await self.get_all_pages("meteringData", params)
    
    async def get_services(self, from_row: int = 0) -> tuple[list[dict], int]:
        """Get list of available services (one page).
        
        Returns:
            Tuple of (services list, next_row). next_row=-1 means no more pages.
        """
        try:
            data = await self._request("GET", "services", params={"fromRow": from_row})
            items = data.get("items", [])
            next_row = data.get("nextRow", -1)
            return items, next_row
        except Exception as e:
            logger.warning(f"Failed to get services: {e}")
            return [], -1
    
    async def get_order_comments(self, order_id: int) -> list[dict]:
        """Get comments for a specific order."""
        try:
            data = await self._request("GET", f"order-comments", params={"orderId": order_id})
            return data.get("items", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.warning(f"Failed to get comments for order {order_id}: {e}")
            return []
    
    async def get_order_details(self, order_id: int) -> dict:
        """
        Get full details for a specific order by ID.
        
        This returns complete data including full customerSummary text
        (which may be truncated in list endpoints).
        
        Args:
            order_id: Order ID
            
        Returns:
            Full order data dict
        """
        try:
            data = await self._request("GET", f"orders/{order_id}/view")
            # Log raw response for debugging
            customer_summary = data.get("customerSummary", "")
            logger.info(f"API /orders/{order_id}/view - customerSummary length: {len(customer_summary)}")
            if len(customer_summary) > 100:
                logger.info(f"API /orders/{order_id}/view - customerSummary preview: {customer_summary[:300]}...")
            return data
        except Exception as e:
            logger.warning(f"Failed to get order details for {order_id}: {e}")
            return {}
    
    async def get_orders_export_columns(self) -> list[dict]:
        """Get list of available columns for orders export."""
        try:
            return await self._request("GET", "orders/export-columns-list")
        except Exception as e:
            logger.warning(f"Failed to get export columns: {e}")
            return []
    
    async def get_acceptance_results(
        self,
        building_id: Optional[int] = None,
        created_at: Optional[str] = None,
    ) -> list[dict]:
        """Get acceptance results (приёмка помещений)."""
        params = {}
        if building_id:
            params["buildingId"] = building_id
        if created_at:
            params["createdAt"] = created_at
        return await self.get_all_pages("acceptance/results", params)
    
    async def get_acceptance_defects(
        self,
        building_id: Optional[int] = None,
    ) -> list[dict]:
        """Get acceptance defects."""
        params = {}
        if building_id:
            params["buildingId"] = building_id
        return await self.get_all_pages("acceptance/form/defects", params)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
