import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class OddsService:
    def __init__(self):
        self.base_url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        self.api_key = settings.ODDS_API_KEY.get_secret_value()

    async def fetch_latest_odds(self) -> list:
        if not self.api_key:
            logger.warning("No ODDS_API_KEY configured, skipping odds fetch")
            return []

        params = {
            "apiKey": self.api_key,
            "regions": "uk,eu",
            "markets": "h2h,totals",
            "oddsFormat": "decimal",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to fetch odds: {e}")
                return []
