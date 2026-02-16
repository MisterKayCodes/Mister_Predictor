from datetime import datetime


class MatchPreprocessor:
    @staticmethod
    def normalize_match_data(api_match: dict) -> dict:
        score = api_match.get("score", {})
        full_time = score.get("fullTime", {}) if score else {}
        half_time = score.get("halfTime", {}) if score else {}

        status_raw = api_match.get("status", "SCHEDULED")
        status = status_raw if status_raw in ("SCHEDULED", "TIMED", "FINISHED") else "SCHEDULED"

        utc_date_str = api_match.get("utcDate", "")
        try:
            utc_date = datetime.fromisoformat(utc_date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            utc_date = datetime.utcnow()

        return {
            "external_id": api_match["id"],
            "utc_date": utc_date,
            "status": status,
            "matchday": api_match.get("matchday"),
            "season": api_match.get("season", {}).get("id") if isinstance(api_match.get("season"), dict) else None,
            "home_team_external_id": api_match.get("homeTeam", {}).get("id"),
            "away_team_external_id": api_match.get("awayTeam", {}).get("id"),
            "home_team_name": api_match.get("homeTeam", {}).get("name", "Unknown"),
            "away_team_name": api_match.get("awayTeam", {}).get("name", "Unknown"),
            "home_team_tla": api_match.get("homeTeam", {}).get("tla", ""),
            "away_team_tla": api_match.get("awayTeam", {}).get("tla", ""),
            "home_score": full_time.get("home"),
            "away_score": full_time.get("away"),
            "home_ht_score": half_time.get("home"),
            "away_ht_score": half_time.get("away"),
        }

    @staticmethod
    def normalize_odds(raw_odds: dict) -> dict:
        h = raw_odds.get("home", 0)
        d = raw_odds.get("draw", 0)
        a = raw_odds.get("away", 0)

        implied_h = 1.0 / h if h > 0 else 0
        implied_d = 1.0 / d if d > 0 else 0
        implied_a = 1.0 / a if a > 0 else 0

        return {
            "home_odds": h,
            "draw_odds": d,
            "away_odds": a,
            "implied_home_prob": round(implied_h, 4),
            "implied_draw_prob": round(implied_d, 4),
            "implied_away_prob": round(implied_a, 4),
        }
