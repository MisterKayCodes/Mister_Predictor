import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class StandingsService:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4/competitions/PL/standings"
        self.headers = {"X-Auth-Token": settings.FOOTBALL_DATA_API_KEY.get_secret_value()}

    async def fetch_current_standings(self):
        """Retrieves the full EPL table for strength analysis."""
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(self.base_url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to fetch standings: {e}")
                return None