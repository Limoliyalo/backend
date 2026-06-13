from typing import Any

import httpx


class OpenFoodFactsClient:
    def __init__(
        self,
        base_url: str,
        user_agent: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._user_agent = user_agent
        self._timeout_seconds = timeout_seconds

    async def get_product(self, barcode: str) -> dict[str, Any] | None:
        url = f"{self._base_url}/api/v3.6/product/{barcode}.json"
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.get(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": self._user_agent,
                },
                params={
                    "fields": "product_name,nutriments",
                },
            )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()
