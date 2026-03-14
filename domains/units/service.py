import asyncio

from domains.api import ApiClient
from domains.units.models import Unit


class UnitService:
    def __init__(self, api: ApiClient | None = None) -> None:
        self.api = api or ApiClient()

    async def close(self) -> None:
        await self.api.close()

    async def load_reference_data(self) -> tuple[list, list, list, list]:
        results = await asyncio.gather(
            self.api.get_eras(),
            self.api.get_factions(),
            self.api.get_types(),
            self.api.get_roles()
        )
        return results

    async def search_units(
        self,
        era_id: int,
        faction_ids: list[int],
        page: int,
        sort_by: str,
        sort_order: str,
        filters: dict | None
    ) -> tuple[list[Unit], int, int]:
        return await self.api.get_units(
            era_id=era_id,
            faction_ids=faction_ids,
            page=page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters
        )
