import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class FootballDataService:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        token = settings.FOOTBALL_DATA_API_KEY.get_secret_value()
        self.headers = {"X-Auth-Token": token} if token else {}

    async def _get(self, endpoint: str) -> dict | None:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            try:
                response = await client.get(f"{self.base_url}/{endpoint}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"API Error: {e.response.status_code} for {endpoint}")
                return None
            except Exception as e:
                logger.error(f"Connection Error: {e}")
                return None

    async def fetch_epl_matches(self, season: str = None) -> dict | None:
        endpoint = "competitions/PL/matches"
        if season:
            endpoint += f"?season={season}"
        return await self._get(endpoint)

    async def fetch_epl_standings(self) -> dict | None:
        return await self._get("competitions/PL/standings")

    async def fetch_team_matches(self, team_id: int) -> dict | None:
        return await self._get(f"teams/{team_id}/matches?status=FINISHED&limit=15")
