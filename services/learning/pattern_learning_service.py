from data.repositories.pattern_stat_repo import PatternStatRepository

class PatternLearningService:
    def __init__(self, pattern_repo: PatternStatRepository):
        self.pattern_repo = pattern_repo

    async def update_pattern_reliability(self, pattern_name: str, won: bool):
        """Tells the Librarian to update success stats for a specific strategy."""
        await self.pattern_repo.update_reliability(pattern_name, won)