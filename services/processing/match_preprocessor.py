from utils.odds import odds_to_implied_prob

class MatchPreprocessor:
    @staticmethod
    def normalize_match_data(api_match: dict) -> dict:
        """Transforms API JSON into our internal Match model format."""
        return {
            "external_id": api_match['id'],
            "utc_date": api_match['utcDate'],
            "status": api_match['status'],
            "home_team_id": api_match['homeTeam']['id'],
            "away_team_id": api_match['awayTeam']['id'],
            "home_score": api_match.get('score', {}).get('fullTime', {}).get('home'),
            "away_score": api_match.get('score', {}).get('fullTime', {}).get('away'),
        }

    @staticmethod
    def process_odds(match_id: int, raw_odds: dict) -> dict:
        """Calculates implied probabilities before storage."""
        h, d, a = raw_odds['home'], raw_odds['draw'], raw_odds['away']
        p_h, p_d, p_a = odds_to_implied_prob(h, d, a)
        
        return {
            "match_id": match_id,
            "home_odds": h,
            "draw_odds": d,
            "away_odds": a,
            "implied_home_prob": p_h,
            "implied_draw_prob": p_d,
            "implied_away_prob": p_a
        }