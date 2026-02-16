import logging
from sqlalchemy.ext.asyncio import AsyncSession
from data.repositories.signal_repo import SignalRepository
from data.repositories.bankroll_repo import BankrollRepository
from data.repositories.pattern_stat_repo import PatternStatRepository

logger = logging.getLogger(__name__)


class PerformanceUpdateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.signal_repo = SignalRepository(session)
        self.bankroll_repo = BankrollRepository(session)
        self.pattern_repo = PatternStatRepository(session)

    async def process_match_result(self, match_id: int, actual_outcome: str):
        signals = await self.signal_repo.get_by_match_id(match_id)
        if not signals:
            return

        total_pnl = 0.0
        total_stake = 0.0
        any_processed = False

        for signal in signals:
            if signal.result_won is None:
                continue

            any_processed = True
            is_win = signal.result_won

            if is_win:
                pnl = signal.recommended_stake * (signal.bookmaker_odds - 1)
            else:
                pnl = -signal.recommended_stake

            total_pnl += pnl
            total_stake += signal.recommended_stake

            if signal.patterns_detected:
                for pattern_name in signal.patterns_detected.split(","):
                    await self.pattern_repo.update_reliability(pattern_name.strip(), is_win)

        if any_processed and total_stake > 0:
            current_bal = await self.bankroll_repo.get_current_balance()
            new_bal = current_bal + total_pnl
            await self.bankroll_repo.update_balance(
                new_balance=new_bal,
                pnl=total_pnl,
                stake=total_stake,
                match_id=match_id,
            )

            logger.info(
                f"Result processed for match {match_id}: "
                f"PnL: {total_pnl:+.2f} | New balance: {new_bal:.2f}"
            )
