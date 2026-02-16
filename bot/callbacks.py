from aiogram import Router, F
from aiogram.types import CallbackQuery
from data.database import AsyncSessionLocal
from data.repositories.signal_repo import SignalRepository
from data.repositories.bankroll_repo import BankrollRepository
from data.repositories.pattern_stat_repo import PatternStatRepository
from data.repositories.match_repo import MatchRepository
from data.repositories.standing_repo import StandingRepository
from data.repositories.odds_repo import OddsRepository
from bot.keyboards.user_menu import get_signal_filter_keyboard, get_signal_details_keyboard
from bot.signal_view_helpers import build_signals_response, group_and_format
from config.risk_config import RISK_PROFILES
from config.settings import settings
import bot.handlers.admin.risk_control as risk_module
from datetime import datetime

router = Router()


@router.callback_query(F.data.startswith("sig_filter:"))
async def signal_filter_callback(callback: CallbackQuery):
    filter_type = callback.data.split(":")[1]

    async with AsyncSessionLocal() as session:
        signal_repo = SignalRepository(session)
        header, signals = await build_signals_response(signal_repo, filter_type)

    results = group_and_format(header, signals)
    keyboard = get_signal_filter_keyboard(active=filter_type)

    await callback.message.edit_text(results[0]["text"], parse_mode="HTML", reply_markup=keyboard)

    for item in results[1:]:
        detail_kb = get_signal_details_keyboard(item["first_signal_id"]) if item["first_signal_id"] else None
        await callback.message.answer(item["text"], parse_mode="HTML", reply_markup=detail_kb)

    await callback.answer()


@router.callback_query(F.data.startswith("signal_detail:"))
async def signal_detail_callback(callback: CallbackQuery):
    signal_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        signal_repo = SignalRepository(session)
        signals = await signal_repo.get_latest(limit=20)
        signal = next((s for s in signals if s.id == signal_id), None)

        if not signal:
            await callback.answer("Signal not found", show_alert=True)
            return

        match = signal.match
        home = match.home_team.name if match and match.home_team else "?"
        away = match.away_team.name if match and match.away_team else "?"

        all_match_signals = [s for s in signals if s.match_id == signal.match_id]
        all_match_signals.sort(key=lambda s: s.rank_in_match or 0)

        from html import escape as h
        from utils.formatters import MARKET_LABELS
        home = h(home)
        away = h(away)

        text = (
            f"<b>Detailed Analysis</b>\n\n"
            f"Match: {home} vs {away}\n\n"
        )

        for i, sig in enumerate(all_match_signals, 1):
            bet_label = MARKET_LABELS.get(sig.suggested_bet, sig.suggested_bet or "")
            text += (
                f"<b>#{i} {h(bet_label)}</b>\n"
                f"  Odds: {sig.bookmaker_odds:.2f}\n"
                f"  Our Model: {(sig.predicted_prob or 0)*100:.1f}%\n"
                f"  Market Implied: {(sig.implied_prob or 0)*100:.1f}%\n"
                f"  Value Edge: {sig.value_edge*100:.1f}%\n"
                f"  Confidence: {sig.confidence_score*100:.1f}%\n"
            )
            if sig.consistency_pct and sig.consistency_pct > 0:
                text += f"  Consistency: {sig.consistency_pct*100:.0f}%\n"
            if sig.recommended_stake > 0:
                text += f"  Stake: ${sig.recommended_stake:.2f}\n"
            if sig.patterns_detected:
                text += f"  Patterns: {h(sig.patterns_detected)}\n"
            if sig.explanation:
                text += f"  <i>{h(sig.explanation)}</i>\n"
            text += "\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("signal_placed:"))
async def signal_placed_callback(callback: CallbackQuery):
    signal_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        signal_repo = SignalRepository(session)
        await signal_repo.mark_published(signal_id)
        await session.commit()

    await callback.answer("Marked as placed!", show_alert=True)


@router.callback_query(F.data == "bankroll_history")
async def bankroll_history_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        bankroll_repo = BankrollRepository(session)
        history = await bankroll_repo.get_history(limit=10)

    if not history:
        await callback.answer("No history yet", show_alert=True)
        return

    text = "*Bankroll History*\n\n"
    for entry in history:
        pnl_sign = "+" if (entry.pnl or 0) >= 0 else ""
        date_str = entry.timestamp.strftime("%m/%d %H:%M") if entry.timestamp else "?"
        text += f"{date_str} | ${entry.balance:.2f} | {pnl_sign}{entry.pnl or 0:.2f}\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "bankroll_reset")
async def bankroll_reset_callback(callback: CallbackQuery):
    await callback.answer("Contact admin to reset bankroll", show_alert=True)


@router.callback_query(F.data == "perf_patterns")
async def perf_patterns_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        pattern_repo = PatternStatRepository(session)
        patterns = await pattern_repo.get_all()

    if not patterns:
        await callback.answer("No pattern data yet", show_alert=True)
        return

    text = "*Pattern Performance*\n\n"
    for p in patterns:
        text += (
            f"*{p.pattern_name}*\n"
            f"  Tested: {p.occurrences} | Wins: {p.wins} | "
            f"Rate: {p.reliability_score*100:.1f}%\n\n"
        )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "perf_recent")
async def perf_recent_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        signal_repo = SignalRepository(session)
        signals = await signal_repo.get_latest(limit=10)

    resolved = [s for s in signals if s.result_won is not None]
    if not resolved:
        await callback.answer("No resolved signals yet", show_alert=True)
        return

    text = "*Recent Results*\n\n"
    for s in resolved[:10]:
        result_icon = "W" if s.result_won else "L"
        text += f"{result_icon} | {s.suggested_bet} @ {s.bookmaker_odds:.2f} | Edge: {s.value_edge*100:.1f}%\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "browse:upcoming")
async def browse_upcoming_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        match_repo = MatchRepository(session)
        matches = await match_repo.get_upcoming()

        if not matches:
            await callback.answer("No upcoming matches found", show_alert=True)
            return

        text = "*Upcoming EPL Matches*\n\n"
        current_md = None
        for m in matches[:20]:
            home = m.home_team.name if m.home_team else "?"
            away = m.away_team.name if m.away_team else "?"
            date_str = m.utc_date.strftime("%b %d, %H:%M") if m.utc_date else "TBD"
            if m.matchday and m.matchday != current_md:
                current_md = m.matchday
                text += f"\n*Matchday {current_md}*\n"
            text += f"  {home} vs {away} - {date_str}\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "browse:results")
async def browse_results_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        match_repo = MatchRepository(session)
        matches = await match_repo.get_recent_finished(limit=15)

        if not matches:
            await callback.answer("No results yet", show_alert=True)
            return

        text = "*Recent EPL Results*\n\n"
        for m in matches:
            home = m.home_team.name if m.home_team else "?"
            away = m.away_team.name if m.away_team else "?"
            hs = m.home_score if m.home_score is not None else "?"
            as_ = m.away_score if m.away_score is not None else "?"
            date_str = m.utc_date.strftime("%b %d") if m.utc_date else ""
            text += f"{date_str} | {home} {hs}-{as_} {away}\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "browse:standings")
async def browse_standings_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        standing_repo = StandingRepository(session)
        standings = await standing_repo.get_latest()

        if not standings:
            await callback.answer("No standings data yet. Run Update Data first.", show_alert=True)
            return

        text = "*EPL Standings*\n\n"
        text += "`Pos Team             P  W  D  L  Pts GD`\n"
        for s in standings:
            name = s.team.name if s.team else "?"
            if len(name) > 16:
                name = name[:15] + "."
            text += (
                f"`{s.position:>2}  {name:<16} {s.played:>2} {s.wins:>2} {s.draws:>2} "
                f"{s.losses:>2} {s.points:>3} {s.goal_diff:>+3}`\n"
            )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "browse:odds")
async def browse_odds_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        match_repo = MatchRepository(session)
        odds_repo = OddsRepository(session)
        upcoming = await match_repo.get_upcoming()

        if not upcoming:
            await callback.answer("No upcoming matches with odds", show_alert=True)
            return

        text = "<b>Live Odds - Upcoming EPL</b>\n\n"
        count = 0
        for m in upcoming[:10]:
            odds = await odds_repo.get_latest_for_match(m.id)
            if not odds:
                continue
            home = m.home_team.name if m.home_team else "?"
            away = m.away_team.name if m.away_team else "?"
            date_str = m.utc_date.strftime("%b %d") if m.utc_date else ""
            text += (
                f"<b>{home} vs {away}</b> ({date_str})\n"
                f"  1X2: H {odds.home_odds:.2f} | D {odds.draw_odds:.2f} | A {odds.away_odds:.2f}\n"
            )
            if odds.over_25_odds and odds.under_25_odds:
                text += f"  O/U 2.5: O {odds.over_25_odds:.2f} | U {odds.under_25_odds:.2f}\n"
            text += "\n"
            count += 1

        if count == 0:
            await callback.answer("No odds data yet. Run Update Data first.", show_alert=True)
            return

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("risk:"))
async def risk_profile_callback(callback: CallbackQuery):
    if callback.from_user.id not in settings.admin_id_list:
        await callback.answer("Admin only", show_alert=True)
        return

    profile_name = callback.data.split(":")[1]

    if profile_name not in RISK_PROFILES:
        await callback.answer("Invalid profile", show_alert=True)
        return

    risk_module.current_profile = profile_name
    profile = RISK_PROFILES[profile_name]

    await callback.answer(f"Risk profile changed to {profile_name.upper()}", show_alert=True)
    await callback.message.answer(
        f"*Risk Profile Updated*\n\n"
        f"New Profile: *{profile_name.upper()}*\n"
        f"Max Picks: {profile['max_picks']}\n"
        f"Min Confidence: {profile['min_confidence']*100:.0f}%\n"
        f"Kelly Fraction: {profile['kelly_fraction']*100:.0f}%",
        parse_mode="Markdown",
    )
