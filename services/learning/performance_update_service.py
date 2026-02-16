from data.repositories.signal_repo import SignalRepository
from data.repositories.bankroll_repo import BankrollRepository

class PerformanceUpdateService:
    def __init__(self, signal_repo: SignalRepository, bankroll_repo: BankrollRepository):
        self.signal_repo = signal_repo
        self.bankroll_repo = bankroll_repo

    async def process_match_result(self, match_id: int, actual_outcome: str):
        """
        Checks if a signal existed for this match and updates PnL.
        Actual outcome: 'HOME_WIN', 'DRAW', or 'AWAY_WIN'
        """
        signal = await self.signal_repo.get_by_match_id(match_id)
        if not signal:
            return

        is_win = (signal.suggested_bet == actual_outcome)
        signal.result_won = is_win
        
        # Calculate PnL based on recommended stake
        pnl = (signal.recommended_stake * (signal.bookmaker_odds - 1)) if is_win else -signal.recommended_stake
        
        current_bal = await self.bankroll_repo.get_current_balance()
        await self.bankroll_repo.update_balance(current_bal + pnl, pnl=pnl)