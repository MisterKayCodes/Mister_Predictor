from data.repositories.signal_repo import SignalRepository
from utils.formatters import format_match_signals_group
from datetime import datetime, timedelta


async def build_signals_response(signal_repo: SignalRepository, filter_type: str) -> tuple[str, list]:
    if filter_type == "matchday":
        next_md = await signal_repo.get_next_matchday_number()
        if next_md:
            signals = await signal_repo.get_by_matchday(next_md)
            header = f"<b>Signals - Matchday {next_md}</b>\n\n"
        else:
            signals = []
            header = ""
    elif filter_type == "3days":
        now = datetime.utcnow()
        end = now + timedelta(days=3)
        signals = await signal_repo.get_by_date_range(now, end)
        header = "<b>Signals - Next 3 Days</b>\n\n"
    elif filter_type == "week":
        now = datetime.utcnow()
        end = now + timedelta(days=7)
        signals = await signal_repo.get_by_date_range(now, end)
        header = "<b>Signals - This Week</b>\n\n"
    else:
        signals = await signal_repo.get_all_upcoming()
        header = "<b>Signals - All Upcoming</b>\n\n"

    return header, signals


def group_and_format(header: str, signals: list) -> list[dict]:
    if not signals:
        return [{
            "text": (
                header + "No signals available for this period.\n\n"
                "Signals are generated during the daily analysis cycle. "
                "Check back after the next update."
            ),
            "first_signal_id": None,
        }]

    grouped = {}
    match_order = []
    for signal in signals:
        mid = signal.match_id
        if mid not in grouped:
            grouped[mid] = {"match_info": None, "signals": []}
            match_order.append(mid)
        match = signal.match
        if grouped[mid]["match_info"] is None and match:
            grouped[mid]["match_info"] = {
                "home": match.home_team.name if match.home_team else "Home",
                "away": match.away_team.name if match.away_team else "Away",
                "match_date": match.utc_date,
                "home_xg": None,
                "away_xg": None,
            }
        grouped[mid]["signals"].append(signal)

    results = []
    match_count = 0
    for mid in match_order:
        data = grouped[mid]
        match_info = data["match_info"] or {"home": "Home", "away": "Away"}
        match_signals = sorted(data["signals"], key=lambda s: s.rank_in_match or 0)

        signals_data = []
        for sig in match_signals:
            signals_data.append({
                "bet_type": sig.suggested_bet,
                "market_key": sig.market_key or "1x2",
                "odds": sig.bookmaker_odds,
                "prob": sig.predicted_prob or sig.confidence_score,
                "edge": sig.value_edge,
                "confidence": sig.confidence_score,
                "consistency": sig.consistency_pct or 0,
                "stake": sig.recommended_stake,
                "has_bookmaker_odds": sig.market_key in ("1x2", "totals"),
            })

        text = format_match_signals_group(match_info, signals_data)
        first_signal = match_signals[0] if match_signals else None

        results.append({
            "text": text,
            "first_signal_id": first_signal.id if first_signal else None,
        })

        match_count += 1
        if match_count >= 10:
            remaining = len(grouped) - match_count
            if remaining > 0:
                results.append({
                    "text": f"<i>...and {remaining} more matches. Use 'All Upcoming' to see all.</i>",
                    "first_signal_id": None,
                })
            break

    return results
