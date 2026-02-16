class FeatureBuilder:
    @staticmethod
    def build_match_features(match, home_history, away_history, standings):
        """
        Transforms raw database records into a Feature Package for the Core Engines.
        """
        # Example feature logic: Form (Last 5 matches)
        home_form = sum([1 for m in home_history[-5:] if m.home_score > m.away_score]) / 5
        away_form = sum([1 for m in away_history[-5:] if m.away_score > m.home_score]) / 5
        
        # Position Gap (Class difference)
        home_pos = next((s.position for s in standings if s.team_id == match.home_team_id), 10)
        away_pos = next((s.position for s in standings if s.team_id == match.away_team_id), 10)
        pos_gap = away_pos - home_pos # Positive means Home is higher ranked
        
        return {
            "match_id": match.id,
            "home_form_avg": home_form,
            "away_form_avg": away_form,
            "position_gap": pos_gap,
            "is_derby": False, # Placeholder for extra logic
        }