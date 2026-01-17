#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.backtest import BacktestEngine
from datetime import datetime, timedelta

def test_fixed_flow():
    """Test the fixed flow"""
    print("Testing fixed backtest flow...")
    
    # Simulate realistic parameters
    symbol = "AAPL"
    data_start = "2024-01-01"
    data_end = "2025-01-17"  # Current date
    entry_date = "2024-06-01"  # Past date within range
    holding_days = 30
    strike_pct = 100
    volatility = 0.25
    interest_rate = 0.05
    strategy_type = "call"
    
    print(f"Parameters:")
    print(f"  Symbol: {symbol}")
    print(f"  Data range: {data_start} to {data_end}")
    print(f"  Entry date: {entry_date}")
    print(f"  Holding days: {holding_days}")
    
    try:
        print("\n1. Creating BacktestEngine...")
        engine = BacktestEngine(
            symbol=symbol,
            start_date=data_start,
            end_date=data_end
        )
        print(f"✓ BacktestEngine created successfully")
        
        print("\n2. Getting entry price from available data...")
        entry_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()
        available_dates = engine.price_data.index.date
        
        # Find the closest available date
        closest_date_idx = None
        min_diff = float('inf')
        
        for i, date in enumerate(available_dates):
            diff = abs((date - entry_date_obj).days)
            if diff < min_diff:
                min_diff = diff
                closest_date_idx = i
        
        if closest_date_idx is not None:
            entry_price = engine.price_data['Close'].iloc[closest_date_idx]
            actual_entry_date = available_dates[closest_date_idx]
            print(f"✓ Entry price: ${entry_price:.2f} on {actual_entry_date}")
            
            strike = entry_price * (strike_pct / 100)
            print(f"  Strike price: ${strike:.2f}")
            
            print("\n3. Running strategy...")
            result = engine.run_strategy(
                strategy_type=strategy_type,
                strike=strike,
                entry_date=entry_date,
                holding_days=holding_days,
                volatility=volatility,
                interest_rate=interest_rate
            )
            print(f"✓ Strategy completed successfully")
            print(f"  P&L: ${result.pnl:.2f} ({result.pnl_pct:.2f}%)")
            print(f"  Entry: ${result.entry_price:.2f} -> Exit: ${result.exit_price:.2f}")
        else:
            print("✗ Could not find suitable entry date")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_flow()