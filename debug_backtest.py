#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.backtest import BacktestEngine
from services.historical_data import HistoricalDataService
from datetime import datetime

def test_backtest():
    print("Testing backtest functionality...")
    
    try:
        # Test historical data service first
        print("\n1. Testing HistoricalDataService...")
        hist_service = HistoricalDataService()
        
        # Test data fetch
        data = hist_service.fetch_data('AAPL', '2024-01-01', '2025-01-17')
        print(f"✓ Data fetched: {len(data)} rows")
        print(f"  Date range: {data.index[0]} to {data.index[-1]}")
        
        # Test current price
        current_price = hist_service.get_current_price('AAPL')
        print(f"✓ Current price: ${current_price:.2f}")
        
        print("\n2. Testing BacktestEngine...")
        # Test backtest engine
        engine = BacktestEngine(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2025-01-17'
        )
        print(f"✓ BacktestEngine initialized")
        print(f"  Price data shape: {engine.price_data.shape}")
        
        print("\n3. Testing strategy with past entry date...")
        # Test with past entry date
        result = engine.run_strategy(
            strategy_type='call',
            strike=200.0,
            entry_date='2024-06-01',
            holding_days=30,
            volatility=0.25,
            interest_rate=0.05
        )
        print(f"✓ Strategy test successful")
        print(f"  P&L: ${result.pnl:.2f} ({result.pnl_pct:.2f}%)")
        
        print("\n4. Testing with future entry date (like user's case)...")
        # Test with future entry date (this might be the issue)
        try:
            result2 = engine.run_strategy(
                strategy_type='call',
                strike=200.0,
                entry_date='2025-02-16',  # Future date like user's
                holding_days=30,
                volatility=0.25,
                interest_rate=0.05
            )
            print(f"✓ Future date test successful")
            print(f"  P&L: ${result2.pnl:.2f} ({result2.pnl_pct:.2f}%)")
        except Exception as e:
            print(f"✗ Future date test failed: {e}")
            print("This is likely the source of the user's error!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backtest()