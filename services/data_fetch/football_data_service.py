import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class FootballDataService:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": settings.FOOTBALL_DATA_API_KEY.get_secret_value()}

    async def _get(self, endpoint: str):
        async with httpx.AsyncClient(headers=self.headers) as client:
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

    async def fetch_epl_matches(self):
        """Fetches all EPL fixtures for the current season."""
        return await self._get("competitions/PL/matches")

    async def fetch_epl_standings(self):
        """Fetches current league table."""
        return await self._get("competitions/PL/standings")