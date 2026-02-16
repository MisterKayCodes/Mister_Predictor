from datetime import datetime
from html import escape
from itertools import groupby


MARKET_LABELS = {
    "HOME_WIN": "Home Win",
    "DRAW": "Draw",
    "AWAY_WIN": "Away Win",
    "OVER_0.5": "Over 0.5 Goals",
    "OVER_1.5": "Over 1.5 Goals",
    "OVER_2.5": "Over 2.5 Goals",
    "OVER_3.5": "Over 3.5 Goals",
    "UNDER_1.5": "Under 1.5 Goals",
    "UNDER_2.5": "Under 2.5 Goals",
    "UNDER_3.5": "Under 3.5 Goals",
    "BTTS_YES": "Both Teams Score - Yes",
    "BTTS_NO": "Both Teams Score - No",
    "CLEAN_SHEET_HOME": "Home Clean Sheet",
    "CLEAN_SHEET_AWAY": "Away Clean Sheet",
    "ODD_GOALS": "Odd Total Goals",
    "EVEN_GOALS": "Even Total Goals",
    "HT_HOME": "Half-Time Home Win",
    "HT_DRAW": "Half-Time Draw",
    "HT_AWAY": "Half-Time Away Win",
    "HT_OVER_0.5": "HT Over 0.5 Goals",
    "HT_OVER_1.5": "HT Over 1.5 Goals",
    "LATE_GOAL": "Late Goal (2nd Half)",
}

MARKET_EMOJIS = {
    "1x2": "&#9917;",
    "totals": "&#128200;",
    "btts": "&#127919;",
    "clean_sheet": "&#128737;",
    "odd_even": "&#127922;",
    "half_time": "&#9201;",
    "late_goal": "&#128165;",
}


def format_signal_message(data: dict) -> str:
    confidence = data.get("confidence", 0)
    if confidence > 0.75:
        indicator = "HIGH CONFIDENCE"
    elif confidence > 0.60:
        indicator = "MODERATE"
    else:
        indicator = "SPECULATIVE"

    match_date = data.get("match_date")
    date_str = ""
    if match_date:
        if isinstance(match_date, datetime):
            date_str = f"\nDate: {match_date.strftime('%d %b, %H:%M UTC')}"
        else:
            date_str = f"\nDate: {match_date}"

    home = escape(str(data['home']))
    away = escape(str(data['away']))
    bet_type = data.get('bet_type', '')
    bet_label = escape(MARKET_LABELS.get(bet_type, bet_type))

    text = (
        f"<b>VALUE SIGNAL DETECTED</b>\n"
        f"Confidence: {indicator}\n\n"
        f"Match: <b>{home}</b> vs <b>{away}</b>{date_str}\n"
        f"Selection: <b>{bet_label}</b>\n"
        f"Odds: {data['odds']:.2f}\n"
        f"Our Prob: {data['prob']*100:.1f}%\n"
        f"Edge: +{data['edge']*100:.1f}%\n"
        f"Rec. Stake: ${data['stake']:.2f}\n"
    )

    explanation = data.get("explanation", "")
    if explanation:
        text += f"\n<i>{escape(explanation)}</i>"

    return text


def format_match_signals_group(match_info: dict, signals_data: list) -> str:
    home = escape(str(match_info.get("home", "Home")))
    away = escape(str(match_info.get("away", "Away")))
    match_date = match_info.get("match_date")
    date_str = ""
    if match_date:
        if isinstance(match_date, datetime):
            date_str = f" | {match_date.strftime('%d %b, %H:%M UTC')}"
        else:
            date_str = f" | {match_date}"

    xg_home = match_info.get("home_xg")
    xg_away = match_info.get("away_xg")
    xg_str = ""
    if xg_home is not None and xg_away is not None:
        xg_str = f"\nxG: {xg_home:.1f} - {xg_away:.1f}"

    text = (
        f"<b>{home} vs {away}</b>{date_str}{xg_str}\n"
        f"<b>Top {len(signals_data)} Value Picks:</b>\n\n"
    )

    for i, sig in enumerate(signals_data, 1):
        bet_type = sig.get("bet_type", "")
        bet_label = MARKET_LABELS.get(bet_type, bet_type)
        market_key = sig.get("market_key", "1x2")
        emoji = MARKET_EMOJIS.get(market_key, "")

        odds = sig.get("odds", 0)
        prob = sig.get("prob", 0)
        edge = sig.get("edge", 0)
        confidence = sig.get("confidence", 0)
        consistency = sig.get("consistency", 0)
        has_bk = sig.get("has_bookmaker_odds", True)

        conf_label = "HIGH" if confidence > 0.75 else "MED" if confidence > 0.60 else "LOW"
        odds_tag = "" if has_bk else " (model)"

        text += (
            f"{emoji} <b>#{i} {escape(bet_label)}</b>{odds_tag}\n"
            f"   Odds: {odds:.2f} | Prob: {prob*100:.0f}% | Edge: +{edge*100:.1f}%\n"
            f"   Conf: {conf_label} ({confidence*100:.0f}%)"
        )
        if consistency and consistency > 0:
            text += f" | Consistency: {consistency*100:.0f}%"
        text += "\n"

        stake = sig.get("stake", 0)
        if stake > 0:
            text += f"   Stake: ${stake:.2f}\n"
        text += "\n"

    return text


def format_bankroll_summary(balance: float, history: list) -> str:
    if not history:
        return f"Bankroll: ${balance:.2f}\nNo transaction history."

    total_pnl = sum(h.pnl or 0 for h in history)
    wins = sum(1 for h in history if (h.pnl or 0) > 0)
    losses = sum(1 for h in history if (h.pnl or 0) < 0)

    return (
        f"Bankroll: ${balance:.2f}\n"
        f"Recent Trades: {len(history)}\n"
        f"Wins: {wins} | Losses: {losses}\n"
        f"Total PnL: {'+'if total_pnl >= 0 else ''}{total_pnl:.2f}"
    )
