import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import sys
import os
import yfinance as yf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.historical_data import HistoricalDataService
from BlackScholes import BlackScholes
class BacktestResult:
    def __init__(self, strategy_type, entry_date, exit_date, entry_price, exit_price,
                 option_entry_value, option_exit_value, pnl, pnl_pct, pnl_series, dates):
        self.strategy_type = strategy_type
        self.entry_date = entry_date
        self.exit_date = exit_date
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.option_entry_value = option_entry_value
        self.option_exit_value = option_exit_value
        self.pnl = pnl
        self.pnl_pct = pnl_pct
        self.pnl_series = pnl_series
        self.dates = dates
class BacktestEngine:
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.hist_service = HistoricalDataService()
        try:
            self.price_data = self.hist_service.fetch_data(symbol, start_date, end_date)
        except ValueError as e:
            # If fetch fails, try with period parameter as fallback
            try:
                ticker = yf.Ticker(symbol)
                self.price_data = ticker.history(period='1y')
                if self.price_data.empty:
                    raise ValueError(f"No data available for {symbol}")
            except Exception as fallback_error:
                raise ValueError(f"Failed to fetch data for {symbol}: {str(e)}")
    def run_strategy(self, strategy_type: str, strike: float, entry_date: str, 
                    holding_days: int, volatility: float, interest_rate: float) -> BacktestResult:
        entry_dt = pd.to_datetime(entry_date)
        
        # Handle timezone consistency
        if self.price_data.index.tz is not None:
            if entry_dt.tz is None:
                entry_dt = entry_dt.tz_localize(self.price_data.index.tz)
        else:
            if entry_dt.tz is not None:
                entry_dt = entry_dt.tz_localize(None)
        
        exit_dt = entry_dt + timedelta(days=holding_days)
        
        # Get nearest indices
        entry_idx = self.price_data.index.get_indexer([entry_dt], method='nearest')[0]
        exit_idx = self.price_data.index.get_indexer([exit_dt], method='nearest')[0]
        
        # Ensure indices are valid
        if entry_idx < 0 or entry_idx >= len(self.price_data):
            entry_idx = max(0, min(entry_idx, len(self.price_data) - 1))
        if exit_idx < 0 or exit_idx >= len(self.price_data):
            exit_idx = max(0, min(exit_idx, len(self.price_data) - 1))
        if entry_idx >= len(self.price_data) or exit_idx >= len(self.price_data):
            raise ValueError("Entry or exit date outside available data range")
        actual_entry_date = self.price_data.index[entry_idx]
        actual_exit_date = self.price_data.index[exit_idx]
        entry_spot = self.price_data['Close'].iloc[entry_idx]
        exit_spot = self.price_data['Close'].iloc[exit_idx]
        days_to_expiry_entry = holding_days
        days_to_expiry_exit = 0
        time_to_maturity_entry = days_to_expiry_entry / 365.0
        time_to_maturity_exit = max(days_to_expiry_exit / 365.0, 0.001)
        bs_entry = BlackScholes(
            time_to_maturity=time_to_maturity_entry,
            strike=strike,
            current_price=entry_spot,
            volatility=volatility,
            interest_rate=interest_rate
        )
        call_entry, put_entry = bs_entry.calculate_prices()
        option_entry_value = call_entry if strategy_type == 'call' else put_entry
        bs_exit = BlackScholes(
            time_to_maturity=time_to_maturity_exit,
            strike=strike,
            current_price=exit_spot,
            volatility=volatility,
            interest_rate=interest_rate
        )
        call_exit, put_exit = bs_exit.calculate_prices()
        option_exit_value = call_exit if strategy_type == 'call' else put_exit
        pnl = option_exit_value - option_entry_value
        pnl_pct = (pnl / option_entry_value) * 100 if option_entry_value > 0 else 0
        pnl_series = []
        dates = []
        for i in range(entry_idx, exit_idx + 1):
            current_date = self.price_data.index[i]
            current_spot = self.price_data['Close'].iloc[i]
            days_remaining = (exit_idx - i)
            time_remaining = max(days_remaining / 365.0, 0.001)
            bs_current = BlackScholes(
                time_to_maturity=time_remaining,
                strike=strike,
                current_price=current_spot,
                volatility=volatility,
                interest_rate=interest_rate
            )
            call_current, put_current = bs_current.calculate_prices()
            option_current_value = call_current if strategy_type == 'call' else put_current
            current_pnl = option_current_value - option_entry_value
            pnl_series.append(current_pnl)
            dates.append(current_date)
        return BacktestResult(
            strategy_type=strategy_type,
            entry_date=actual_entry_date,
            exit_date=actual_exit_date,
            entry_price=entry_spot,
            exit_price=exit_spot,
            option_entry_value=option_entry_value,
            option_exit_value=option_exit_value,
            pnl=pnl,
            pnl_pct=pnl_pct,
            pnl_series=pnl_series,
            dates=dates
        )
    def calculate_metrics(self, pnl_series: List[float]) -> Dict:
        pnl_array = np.array(pnl_series)
        max_pnl = np.max(pnl_array)
        min_pnl = np.min(pnl_array)
        final_pnl = pnl_array[-1]
        cumulative = np.maximum.accumulate(pnl_array)
        drawdown = cumulative - pnl_array
        max_drawdown = np.max(drawdown)
        if len(pnl_array) > 1:
            returns = np.diff(pnl_array)
            volatility = np.std(returns)
        else:
            volatility = 0
        return {
            'max_pnl': float(max_pnl),
            'min_pnl': float(min_pnl),
            'final_pnl': float(final_pnl),
            'max_drawdown': float(max_drawdown),
            'volatility': float(volatility)
        }
