"""Test script to verify all imports work correctly"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    print("✓ Testing BlackScholes...")
    from BlackScholes import BlackScholes
    
    print("✓ Testing components.heatmap...")
    from components.heatmap import HeatmapGenerator
    
    print("✓ Testing components.greeks...")
    from components.greeks import GreeksCalculator
    
    print("✓ Testing components.common...")
    from components.common import render_footer
    
    print("✓ Testing database.db_service...")
    from database.db_service import DatabaseService
    
    print("✓ Testing services.backtest...")
    from services.backtest import BacktestEngine
    
    print("✓ Testing services.historical_data...")
    from services.historical_data import HistoricalDataService
    
    print("✓ Testing api.main...")
    from api.main import app
    
    print("✓ Testing api.models...")
    from api.models import OptionPriceRequest
    
    print("\n✅ ALL IMPORTS SUCCESSFUL!")
    print("\nYour Black-Scholes app is ready to run!")
    print("Run: streamlit run streamlit_app.py")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
