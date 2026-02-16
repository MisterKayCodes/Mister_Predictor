import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class OddsService:
    def __init__(self):
        # Example using The-Odds-API or similar
        self.base_url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        self.api_key = os.getenv("ODDS_API_KEY") 

    async def fetch_latest_odds(self):
        """
        Fetches the latest 1X2 market prices for all upcoming EPL games.
        """
        params = {
            "apiKey": self.api_key,
            "regions": "uk,eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to fetch odds: {e}")
                return []