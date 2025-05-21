import httpx
import os
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Environment variables
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")


class ProductServiceClient:
    """
    Client for communicating with the Product Service API.
    """

    def __init__(self, base_url: str = PRODUCT_SERVICE_URL):
        self.base_url = base_url
        logger.info(f"ProductServiceClient initialized with URL: {base_url}")

    async def get_bike(self, bike_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a bike's details from the product service.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/bikes/{bike_id}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error retrieving bike {bike_id}: {e.response.status_code}"
            )
            return None
        except Exception as e:
            logger.error(f"Error retrieving bike {bike_id}: {str(e)}")
            return None

    async def mark_bike_as_bought(self, bike_id: int) -> bool:
        """
        Mark a bike as bought in the product service.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/bikes/{bike_id}/mark_as_bought"
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error marking bike {bike_id} as bought: {str(e)}")
            return False

    async def sync_bike(self, bike_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a bike from the product service and sync it to our local database.
        """
        return await self.get_bike(bike_id)
