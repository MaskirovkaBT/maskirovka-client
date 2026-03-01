from typing import TypeVar

import httpx
from pydantic import TypeAdapter

from domains.era import Era
from domains.faction import Faction
from domains.settings import settings
from domains.unit import Unit

T = TypeVar("T")


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.api_base_url

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=30.0
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise ApiError(f'HTTP {e.response.status_code}: {e.response.text}') from e
            return response.json()

    async def _fetch_list(
        self,
        endpoint: str,
        model_class: type[T]
    ) -> list[T]:
        data = await self._get(endpoint)
        items = TypeAdapter(list[model_class]).validate_python(data)
        return items

    async def get_eras(self) -> list[Era]:
        return await self._fetch_list("/eras", Era)

    async def get_factions(self) -> list[Faction]:
        return await self._fetch_list("/factions", Faction)

    async def get_units(
        self,
        era_id: int,
        faction_id: int,
        page: int = 1
    ) -> tuple[list[Unit], int, int]:
        data = await self._get(
            "/units",
            params={"era_id": era_id, "faction_id": faction_id, "page": page}
        )

        items = data.get("items", [])
        units = TypeAdapter(list[Unit]).validate_python(items)

        current_page = data.get("page", page)
        total_pages = data.get("pages", 1)

        return units, current_page, total_pages
