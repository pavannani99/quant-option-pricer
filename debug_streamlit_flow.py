#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.backtest import BacktestEngine
from services.historical_data import HistoricalDataService
from datetime import datetime, timedelta

def test_streamlit_flow():
    """Test the exact flow that Streamlit is using"""
    print("Testing Streamlit backtest flow...")
    
    # Simulate the exact parameters from the user's screenshot
    symbol = "AAPL"
    data_start = "2024-01-01"
    data_end = "2025-12-31"
    entry_date = "2025-02-16"
    holding_days = 1  # From the screenshot
    strike_pct = 100  # 100% of entry price
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
        print(f"  Data shape: {engine.price_data.shape}")
        print(f"  Data range: {engine.price_data.index[0]} to {engine.price_data.index[-1]}")
        
        print("\n2. Fetching entry price...")
        hist_service = HistoricalDataService()
        
        # This is the exact call from the Streamlit code
        entry_data = hist_service.fetch_data(
            symbol, 
            entry_date, 
            (datetime.strptime(entry_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        )
        print(f"✓ Entry data fetched: {len(entry_data)} rows")
        
        if len(entry_data) > 0:
            entry_price = entry_data['Close'].iloc[0]
            print(f"  Entry price: ${entry_price:.2f}")
            
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
        else:
            print("✗ No entry data found!")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streamlit_flow()