RISK_PROFILES = {
    "conservative": {
        "max_picks": 3,
        "min_confidence": 0.70,
        "min_value_edge": 0.08,
        "kelly_fraction": 0.05,
        "max_stake_pct": 0.03,
    },
    "balanced": {
        "max_picks": 5,
        "min_confidence": 0.60,
        "min_value_edge": 0.05,
        "kelly_fraction": 0.10,
        "max_stake_pct": 0.05,
    },
    "aggressive": {
        "max_picks": 8,
        "min_confidence": 0.50,
        "min_value_edge": 0.03,
        "kelly_fraction": 0.15,
        "max_stake_pct": 0.08,
    },
}

DEFAULT_RISK_PROFILE = "balanced"
