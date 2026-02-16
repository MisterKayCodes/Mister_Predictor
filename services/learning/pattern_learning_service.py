import logging
from data.repositories.pattern_stat_repo import PatternStatRepository

logger = logging.getLogger(__name__)


class PatternLearningService:
    def __init__(self, pattern_repo: PatternStatRepository):
        self.pattern_repo = pattern_repo

    async def update_pattern_reliability(self, pattern_name: str, won: bool):
        stat = await self.pattern_repo.update_reliability(pattern_name, won)
        logger.info(
            f"Pattern '{pattern_name}' updated: "
            f"{stat.wins}/{stat.occurrences} "
            f"({stat.reliability_score*100:.1f}% reliability)"
        )
        return stat
