import httpx
import os
import logging
import asyncio
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Environment variables
mode = os.getenv("mode", "production").lower()
PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    (
        "http://localhost:8001"
        if mode == "development"
        else "https://product-service.fly.dev"
    ),
)


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
        # Add retry logic
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    logger.info(
                        f"Attempt {attempt + 1}/{max_retries + 1}: Requesting bike {bike_id} from {self.base_url}/api/bikes/{bike_id}"
                    )
                    response = await client.get(f"{self.base_url}/api/bikes/{bike_id}")
                    response.raise_for_status()
                    logger.info(f"Successfully retrieved bike {bike_id}")
                    return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error retrieving bike {bike_id}: {e.response.status_code}"
                )
                # Don't retry on 404
                if e.response.status_code == 404:
                    return None
                # Retry on other errors
                if attempt < max_retries:
                    wait_time = retry_delay * (2**attempt)
                    logger.warning(f"Will retry in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached for bike {bike_id}")
                    return None
            except Exception as e:
                logger.error(f"Error retrieving bike {bike_id}: {str(e)}")
                if attempt < max_retries:
                    wait_time = retry_delay * (2**attempt)
                    logger.warning(f"Will retry in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached for bike {bike_id}")
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
