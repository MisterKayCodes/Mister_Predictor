import logging
from data.repositories.match_repo import MatchRepository
from services.processing.feature_builder import FeatureBuilder

logger = logging.getLogger(__name__)

class SignalPipelineService:
    def __init__(self, match_repo: MatchRepository, core_engine):
        self.match_repo = match_repo
        self.core = core_engine
        self.feature_builder = FeatureBuilder()

    async def execute_full_analysis(self):
        """The main workflow that generates daily betting signals."""
        # 1. Get all upcoming matches
        matches = await self.match_repo.get_upcoming_matches()
        
        for match in matches:
            # 2. Build the Feature Package
            # (In reality, we'd fetch team history here via repos)
            features = self.feature_builder.build_match_features(match, [], [], [])
            
            # 3. Hand off to the Brain (Core Engine)
            # This is where logic happens in Phase 4
            prediction = self.core.generate_prediction(features)
            
            if prediction['is_value']:
                logger.info(f"VALUE DETECTED: {match.id} - {prediction['recommendation']}")
                # 4. Store the resulting Signal in the Vault