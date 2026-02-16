import math


class ProbabilityEngine:
    def _poisson_prob(self, lam: float, k: int) -> float:
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return (lam ** k) * math.exp(-lam) / math.factorial(k)

    def _poisson_grid(self, home_xg: float, away_xg: float, max_goals: int = 7) -> list[list[float]]:
        grid = []
        for h in range(max_goals + 1):
            row = []
            for a in range(max_goals + 1):
                row.append(self._poisson_prob(home_xg, h) * self._poisson_prob(away_xg, a))
            grid.append(row)
        return grid

    def calculate_probs(self, features: dict) -> dict:
        home_form = features.get("home_form_avg", 0.4)
        away_form = features.get("away_form_avg", 0.3)
        position_gap = features.get("position_gap", 0)
        home_scored_avg = features.get("home_scored_avg", 1.2)
        away_scored_avg = features.get("away_scored_avg", 1.0)
        home_conceded_avg = features.get("home_conceded_avg", 1.0)
        away_conceded_avg = features.get("away_conceded_avg", 1.3)
        defensive_strength = features.get("defensive_strength", 0.5)

        league_avg_home = 1.45
        league_avg_away = 1.15

        home_att = (home_scored_avg / league_avg_home) if league_avg_home > 0 else 1.0
        home_def = (home_conceded_avg / league_avg_away) if league_avg_away > 0 else 1.0
        away_att = (away_scored_avg / league_avg_away) if league_avg_away > 0 else 1.0
        away_def = (away_conceded_avg / league_avg_home) if league_avg_home > 0 else 1.0

        home_xg = home_att * away_def * league_avg_home
        away_xg = away_att * home_def * league_avg_away

        form_adj = (home_form - 0.4) * 0.3 - (away_form - 0.3) * 0.2
        pos_adj = position_gap * 0.02
        home_xg = max(0.3, home_xg + form_adj + pos_adj * 0.1)
        away_xg = max(0.3, away_xg - form_adj - pos_adj * 0.1)

        grid = self._poisson_grid(home_xg, away_xg)
        mg = len(grid)

        grid_total = sum(grid[h][a] for h in range(mg) for a in range(mg))

        home_win = sum(grid[h][a] for h in range(mg) for a in range(mg) if h > a) / grid_total
        draw = sum(grid[h][a] for h in range(mg) for a in range(mg) if h == a) / grid_total
        away_win = sum(grid[h][a] for h in range(mg) for a in range(mg) if h < a) / grid_total

        under_1 = sum(grid[h][a] for h in range(mg) for a in range(mg) if h + a <= 0) / grid_total
        under_2 = sum(grid[h][a] for h in range(mg) for a in range(mg) if h + a <= 1) / grid_total
        under_3 = sum(grid[h][a] for h in range(mg) for a in range(mg) if h + a <= 2) / grid_total
        under_4 = sum(grid[h][a] for h in range(mg) for a in range(mg) if h + a <= 3) / grid_total

        over_05 = 1.0 - under_1
        over_15 = 1.0 - under_2
        over_25 = 1.0 - under_3
        over_35 = 1.0 - under_4

        home_scores_zero = sum(grid[0][a] for a in range(mg)) / grid_total
        away_scores_zero = sum(grid[h][0] for h in range(mg)) / grid_total
        btts_yes = 1.0 - home_scores_zero - away_scores_zero + (grid[0][0] / grid_total)
        btts_no = 1.0 - btts_yes

        clean_sheet_home = away_scores_zero
        clean_sheet_away = home_scores_zero

        odd_goals = sum(grid[h][a] for h in range(mg) for a in range(mg) if (h + a) % 2 == 1) / grid_total
        even_goals = 1.0 - odd_goals

        ht_home_xg = home_xg * 0.42
        ht_away_xg = away_xg * 0.42
        ht_grid = self._poisson_grid(ht_home_xg, ht_away_xg, max_goals=5)
        ht_mg = len(ht_grid)
        ht_grid_total = sum(ht_grid[h][a] for h in range(ht_mg) for a in range(ht_mg))

        ht_home_win = sum(ht_grid[h][a] for h in range(ht_mg) for a in range(ht_mg) if h > a) / ht_grid_total
        ht_draw = sum(ht_grid[h][a] for h in range(ht_mg) for a in range(ht_mg) if h == a) / ht_grid_total
        ht_away_win = sum(ht_grid[h][a] for h in range(ht_mg) for a in range(ht_mg) if h < a) / ht_grid_total

        ht_over_05 = 1.0 - (ht_grid[0][0] / ht_grid_total)
        ht_over_15 = 1.0 - sum(ht_grid[h][a] for h in range(ht_mg) for a in range(ht_mg) if h + a <= 1) / ht_grid_total

        second_half_xg = (home_xg + away_xg) * 0.58
        late_goal_prob = 1.0 - math.exp(-second_half_xg * 0.4)

        return {
            "home": round(home_win, 4),
            "draw": round(draw, 4),
            "away": round(away_win, 4),
            "over_05": round(over_05, 4),
            "over_15": round(over_15, 4),
            "over_25": round(over_25, 4),
            "over_35": round(over_35, 4),
            "btts_yes": round(btts_yes, 4),
            "btts_no": round(btts_no, 4),
            "clean_sheet_home": round(clean_sheet_home, 4),
            "clean_sheet_away": round(clean_sheet_away, 4),
            "odd_goals": round(odd_goals, 4),
            "even_goals": round(even_goals, 4),
            "ht_home": round(ht_home_win, 4),
            "ht_draw": round(ht_draw, 4),
            "ht_away": round(ht_away_win, 4),
            "ht_over_05": round(ht_over_05, 4),
            "ht_over_15": round(ht_over_15, 4),
            "late_goal": round(late_goal_prob, 4),
            "home_xg": round(home_xg, 2),
            "away_xg": round(away_xg, 2),
        }
