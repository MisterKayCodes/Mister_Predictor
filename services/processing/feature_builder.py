class FeatureBuilder:
    @staticmethod
    def build_match_features(match, home_history: list, away_history: list, standings: list) -> dict:
        home_form = 0.4
        if home_history:
            recent = home_history[-5:]
            wins = sum(1 for m in recent if m.home_score is not None and m.home_score > m.away_score)
            home_form = wins / len(recent) if recent else 0.4

        away_form = 0.3
        if away_history:
            recent = away_history[-5:]
            wins = sum(1 for m in recent if m.away_score is not None and m.away_score > m.home_score)
            away_form = wins / len(recent) if recent else 0.3

        home_pos = 10
        away_pos = 10
        for s in standings:
            if s.team_id == match.home_team_id:
                home_pos = s.position or 10
            if s.team_id == match.away_team_id:
                away_pos = s.position or 10

        pos_gap = away_pos - home_pos

        goals_avg = 1.3
        if home_history:
            total_goals = sum(
                (m.home_score or 0) + (m.away_score or 0)
                for m in home_history[-5:]
            )
            goals_avg = total_goals / min(5, len(home_history))

        defensive_strength = 0.5
        if home_history:
            conceded = sum(m.away_score or 0 for m in home_history[-5:])
            defensive_strength = max(0.1, min(0.9, 1 - (conceded / (min(5, len(home_history)) * 2))))

        home_scored_avg = 1.2
        away_scored_avg = 1.0
        home_conceded_avg = 1.0
        away_conceded_avg = 1.3
        if home_history:
            n = min(5, len(home_history))
            recent_h = home_history[-n:]
            home_scored_avg = sum(m.home_score or 0 for m in recent_h) / n
            home_conceded_avg = sum(m.away_score or 0 for m in recent_h) / n
        if away_history:
            n = min(5, len(away_history))
            recent_a = away_history[-n:]
            away_scored_avg = sum(m.away_score or 0 for m in recent_a) / n
            away_conceded_avg = sum(m.home_score or 0 for m in recent_a) / n

        btts_home_rate = 0.5
        btts_away_rate = 0.5
        clean_sheet_home_rate = 0.3
        clean_sheet_away_rate = 0.2
        over_25_home_rate = 0.5
        over_15_home_rate = 0.7
        over_35_home_rate = 0.3

        ht_home_scored_avg = 0.5
        ht_home_conceded_avg = 0.4
        ht_away_scored_avg = 0.4
        ht_away_conceded_avg = 0.5
        ht_goals_avg = 0.9

        late_goal_home_rate = 0.3
        late_goal_away_rate = 0.3

        if home_history:
            n = min(5, len(home_history))
            recent_h = home_history[-n:]
            finished_h = [m for m in recent_h if m.home_score is not None and m.away_score is not None]
            if finished_h:
                fn = len(finished_h)
                btts_home_rate = sum(1 for m in finished_h if m.home_score > 0 and m.away_score > 0) / fn
                clean_sheet_home_rate = sum(1 for m in finished_h if m.away_score == 0) / fn
                over_25_home_rate = sum(1 for m in finished_h if (m.home_score + m.away_score) > 2) / fn
                over_15_home_rate = sum(1 for m in finished_h if (m.home_score + m.away_score) > 1) / fn
                over_35_home_rate = sum(1 for m in finished_h if (m.home_score + m.away_score) > 3) / fn

                ht_h = [m for m in finished_h if m.home_ht_score is not None and m.away_ht_score is not None]
                if ht_h:
                    htn = len(ht_h)
                    ht_home_scored_avg = sum(m.home_ht_score for m in ht_h) / htn
                    ht_home_conceded_avg = sum(m.away_ht_score for m in ht_h) / htn
                    ht_goals_avg = sum(m.home_ht_score + m.away_ht_score for m in ht_h) / htn
                    late_goal_home_rate = sum(
                        1 for m in ht_h
                        if (m.home_score + m.away_score) - (m.home_ht_score + m.away_ht_score) > 0
                        and (m.home_score + m.away_score) > (m.home_ht_score + m.away_ht_score) + 1
                    ) / htn

        if away_history:
            n = min(5, len(away_history))
            recent_a = away_history[-n:]
            finished_a = [m for m in recent_a if m.home_score is not None and m.away_score is not None]
            if finished_a:
                fn = len(finished_a)
                btts_away_rate = sum(1 for m in finished_a if m.home_score > 0 and m.away_score > 0) / fn
                clean_sheet_away_rate = sum(1 for m in finished_a if m.home_score == 0) / fn

                ht_a = [m for m in finished_a if m.home_ht_score is not None and m.away_ht_score is not None]
                if ht_a:
                    htn = len(ht_a)
                    ht_away_scored_avg = sum(m.away_ht_score for m in ht_a) / htn
                    ht_away_conceded_avg = sum(m.home_ht_score for m in ht_a) / htn
                    late_goal_away_rate = sum(
                        1 for m in ht_a
                        if (m.home_score + m.away_score) - (m.home_ht_score + m.away_ht_score) > 0
                        and (m.home_score + m.away_score) > (m.home_ht_score + m.away_ht_score) + 1
                    ) / htn

        odd_goals_rate = 0.5
        all_finished = []
        for m in (home_history or [])[-5:]:
            if m.home_score is not None and m.away_score is not None:
                all_finished.append(m)
        for m in (away_history or [])[-5:]:
            if m.home_score is not None and m.away_score is not None:
                all_finished.append(m)
        if all_finished:
            odd_goals_rate = sum(1 for m in all_finished if (m.home_score + m.away_score) % 2 == 1) / len(all_finished)

        return {
            "match_id": match.id,
            "home_form_avg": home_form,
            "away_form_avg": away_form,
            "position_gap": pos_gap,
            "goals_avg": goals_avg,
            "defensive_strength": defensive_strength,
            "home_scored_avg": home_scored_avg,
            "away_scored_avg": away_scored_avg,
            "home_conceded_avg": home_conceded_avg,
            "away_conceded_avg": away_conceded_avg,
            "btts_home_rate": btts_home_rate,
            "btts_away_rate": btts_away_rate,
            "clean_sheet_home_rate": clean_sheet_home_rate,
            "clean_sheet_away_rate": clean_sheet_away_rate,
            "over_25_home_rate": over_25_home_rate,
            "over_15_home_rate": over_15_home_rate,
            "over_35_home_rate": over_35_home_rate,
            "ht_home_scored_avg": ht_home_scored_avg,
            "ht_home_conceded_avg": ht_home_conceded_avg,
            "ht_away_scored_avg": ht_away_scored_avg,
            "ht_away_conceded_avg": ht_away_conceded_avg,
            "ht_goals_avg": ht_goals_avg,
            "late_goal_home_rate": late_goal_home_rate,
            "late_goal_away_rate": late_goal_away_rate,
            "odd_goals_rate": odd_goals_rate,
        }
