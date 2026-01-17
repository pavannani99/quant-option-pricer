#!/usr/bin/env python3
import yfinance as yf
from datetime import datetime, timedelta

print("Testing yfinance connectivity...")

# Test 1: Simple ticker info
print("\n1. Testing ticker info fetch...")
try:
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    print(f"✓ Ticker info retrieved: {info.get('shortName', 'N/A')}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Historical data with recent dates
print("\n2. Testing historical data (last 30 days)...")
try:
    end = datetime.now()
    start = end - timedelta(days=30)
    ticker = yf.Ticker("AAPL")
    df = ticker.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
    print(f"✓ Data retrieved: {len(df)} rows")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")
    print(f"  Latest close: ${df['Close'].iloc[-1]:.2f}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Historical data with 1 year range
print("\n3. Testing historical data (1 year)...")
try:
    end = datetime.now()
    start = end - timedelta(days=365)
    ticker = yf.Ticker("AAPL")
    df = ticker.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
    print(f"✓ Data retrieved: {len(df)} rows")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Using period parameter
print("\n4. Testing with period parameter...")
try:
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period='1y')
    print(f"✓ Data retrieved: {len(df)} rows")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nDiagnostics complete.")
