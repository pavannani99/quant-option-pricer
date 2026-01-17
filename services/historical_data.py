import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
class HistoricalDataService:
    def __init__(self):
        self.cache = {}
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        cache_key = f"{symbol}_{start_date}_{end_date}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol} between {start_date} and {end_date}. Please verify the symbol is correct and dates are not in the future.")
            self.cache[cache_key] = df
            return df
        except Exception as e:
            raise ValueError(f"Error fetching data for {symbol}: {str(e)}")
    def calculate_historical_volatility(self, prices: pd.DataFrame, window: int = None) -> float:
        if 'Close' not in prices.columns:
            raise ValueError("DataFrame must contain 'Close' column")
        if window:
            close_prices = prices['Close'].tail(window)
        else:
            close_prices = prices['Close']
        log_returns = np.log(close_prices / close_prices.shift(1))
        volatility = log_returns.std() * np.sqrt(252)
        return volatility
    def get_current_price(self, symbol: str) -> float:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='5d')
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            return df['Close'].iloc[-1]
        except Exception as e:
            raise ValueError(f"Error fetching current price for {symbol}: {str(e)}")
    def get_price_statistics(self, prices: pd.DataFrame) -> dict:
        close_prices = prices['Close']
        return {
            'mean': close_prices.mean(),
            'std': close_prices.std(),
            'min': close_prices.min(),
            'max': close_prices.max(),
            'current': close_prices.iloc[-1],
            'change': close_prices.iloc[-1] - close_prices.iloc[0],
            'change_pct': ((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100
        }
    def validate_symbol(self, symbol: str) -> bool:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except:
            return False
