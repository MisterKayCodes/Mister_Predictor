class PatternEngine:
    def detect_patterns(self, home_history: list, away_history: list, features: dict = None) -> list[dict]:
        patterns = []

        if len(home_history) >= 3:
            finished_home = [m for m in home_history[-5:] if m.home_score is not None and m.away_score is not None]

            home_losses = [m for m in finished_home if m.home_score < m.away_score]
            if len(home_losses) >= 3:
                patterns.append({
                    "name": "HOME_COLD_STREAK",
                    "strength": 0.7,
                    "description": "Home team lost last 3+ home games",
                })

            home_wins = [m for m in finished_home if m.home_score > m.away_score]
            if len(home_wins) >= 4:
                patterns.append({
                    "name": "HOME_FORTRESS",
                    "strength": 0.8,
                    "description": "Home team won 4+ of last 5 home games",
                })

            high_scoring = [m for m in finished_home if (m.home_score + m.away_score) > 2]
            if len(high_scoring) >= 4:
                patterns.append({
                    "name": "HIGH_SCORING_HOME",
                    "strength": 0.65,
                    "description": "Over 2.5 goals in 4+ of last 5 home games",
                    "markets": ["OVER_2.5", "BTTS_YES"],
                })

            low_scoring = [m for m in finished_home if (m.home_score + m.away_score) <= 2]
            if len(low_scoring) >= 4:
                patterns.append({
                    "name": "LOW_SCORING_HOME",
                    "strength": 0.65,
                    "description": "Under 2.5 goals in 4+ of last 5 home games",
                    "markets": ["UNDER_2.5"],
                })

            btts_yes = [m for m in finished_home if m.home_score > 0 and m.away_score > 0]
            if len(btts_yes) >= 4:
                patterns.append({
                    "name": "BTTS_HOME_TREND",
                    "strength": 0.7,
                    "description": "Both teams scored in 4+ of last 5 home games",
                    "markets": ["BTTS_YES"],
                })

            clean_sheets = [m for m in finished_home if m.away_score == 0]
            if len(clean_sheets) >= 3:
                patterns.append({
                    "name": "HOME_CLEAN_SHEET_MACHINE",
                    "strength": 0.75,
                    "description": "Home team kept clean sheet in 3+ of last 5 home games",
                    "markets": ["CLEAN_SHEET_HOME", "BTTS_NO", "UNDER_2.5"],
                })

            ht_home = [m for m in finished_home if m.home_ht_score is not None and m.away_ht_score is not None]
            if len(ht_home) >= 3:
                ht_leading = [m for m in ht_home if m.home_ht_score > m.away_ht_score]
                if len(ht_leading) >= 3:
                    patterns.append({
                        "name": "HOME_FAST_STARTER",
                        "strength": 0.7,
                        "description": "Home team leads at HT in 3+ of last 5 home games",
                        "markets": ["HT_HOME"],
                    })

                ht_goals = [m for m in ht_home if (m.home_ht_score + m.away_ht_score) > 0]
                if len(ht_goals) >= 4:
                    patterns.append({
                        "name": "FIRST_HALF_GOALS",
                        "strength": 0.65,
                        "description": "Goals in 1st half in 4+ of last 5 home games",
                        "markets": ["HT_OVER_0.5"],
                    })

                late_goals = [
                    m for m in ht_home
                    if (m.home_score + m.away_score) > (m.home_ht_score + m.away_ht_score) + 1
                ]
                if len(late_goals) >= 3:
                    patterns.append({
                        "name": "LATE_SURGE",
                        "strength": 0.6,
                        "description": "2+ second half goals in 3+ of last 5 home games",
                        "markets": ["LATE_GOAL"],
                    })

        if len(away_history) >= 3:
            finished_away = [m for m in away_history[-5:] if m.home_score is not None and m.away_score is not None]

            away_losses = [m for m in finished_away if m.away_score < m.home_score]
            if len(away_losses) >= 4:
                patterns.append({
                    "name": "AWAY_WEAKNESS",
                    "strength": 0.7,
                    "description": "Away team lost 4+ of last 5 away games",
                })

            away_concedes = [m for m in finished_away if m.home_score > 0]
            if len(away_concedes) >= 4:
                patterns.append({
                    "name": "AWAY_LEAKY_DEFENSE",
                    "strength": 0.6,
                    "description": "Away team conceded in 4+ of last 5 away games",
                    "markets": ["BTTS_YES", "OVER_2.5"],
                })

            away_clean_sheets = [m for m in finished_away if m.home_score == 0]
            if len(away_clean_sheets) >= 3:
                patterns.append({
                    "name": "AWAY_CLEAN_SHEET_MACHINE",
                    "strength": 0.7,
                    "description": "Away team kept clean sheet in 3+ of last 5 away games",
                    "markets": ["CLEAN_SHEET_AWAY"],
                })

            away_btts = [m for m in finished_away if m.home_score > 0 and m.away_score > 0]
            if len(away_btts) >= 4:
                patterns.append({
                    "name": "BTTS_AWAY_TREND",
                    "strength": 0.65,
                    "description": "Both teams scored in 4+ of last 5 away games",
                    "markets": ["BTTS_YES"],
                })

        if features:
            pos_gap = features.get("position_gap", 0)
            if pos_gap >= 8:
                patterns.append({
                    "name": "CLASS_GAP",
                    "strength": 0.75,
                    "description": f"Large position gap: {pos_gap} places",
                })
            elif pos_gap <= -8:
                patterns.append({
                    "name": "GIANT_KILLER_SCENARIO",
                    "strength": 0.5,
                    "description": "Lower-ranked home team vs top side",
                })

        return patterns
