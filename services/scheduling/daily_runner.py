import asyncio
import logging

logger = logging.getLogger(__name__)

class DailyRunner:
    def __init__(self, pipeline_service):
        self.pipeline = pipeline_service

    async def run_daily_cycle(self):
        """The 5:00 AM Routine"""
        logger.info("Starting Daily Intelligence Cycle...")
        
        # 1. Fetch Data
        # 2. Update Results
        # 3. Analyze New Matches
        # 4. Generate Signals
        
        await self.pipeline.execute_full_analysis()
        logger.info("Daily Cycle Complete.")

    async def start_scheduler(self):
        """Simple loop to run once every 24 hours."""
        while True:
            await self.run_daily_cycle()
            await asyncio.sleep(86400) # Wait 24 hours