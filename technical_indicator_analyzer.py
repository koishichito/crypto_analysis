import pandas as pd
import numpy as np
import os
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator

# Import coin list from config
from config import COINS

# Directory settings
DATA_DIR = "data"
ANALYSIS_DIR = "analysis"
os.makedirs(ANALYSIS_DIR, exist_ok=True)

def calculate_technical_indicators(df):
    """
    Calculate technical indicators
    
    Args:
        df: DataFrame containing price data
        
    Returns:
        DataFrame: DataFrame with added technical indicators
    """
    if df is None or df.empty:
        return None
    
    # Check if required columns exist
    required_columns = ["close", "high", "low", "open", "volume"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Required column {col} not found in DataFrame")
            return None
    
    # RSI (Relative Strength Index)
    rsi = RSIIndicator(close=df["close"], window=14)
    df["rsi"] = rsi.rsi()
    
    # MACD (Moving Average Convergence Divergence)
    macd = MACD(close=df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()
    
    # Bollinger Bands
    bollinger = BollingerBands(close=df["close"])
    df["bb_upper"] = bollinger.bollinger_hband()
    df["bb_middle"] = bollinger.bollinger_mavg()
    df["bb_lower"] = bollinger.bollinger_lband()
    
    # Moving Averages
    df["sma_20"] = SMAIndicator(close=df["close"], window=20).sma_indicator()
    df["sma_50"] = SMAIndicator(close=df["close"], window=50).sma_indicator()
    df["ema_12"] = EMAIndicator(close=df["close"], window=12).ema_indicator()
    df["ema_26"] = EMAIndicator(close=df["close"], window=26).ema_indicator()
    
    # Stochastics
    stoch = StochasticOscillator(high=df["high"], low=df["low"], close=df["close"])
    df["stoch_k"] = stoch.stoch()
    df["stoch_d"] = stoch.stoch_signal()
    
    # Volume Indicators
    df["obv"] = OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"]).on_balance_volume()
    
    # Price Change Percentage (%)
    df["price_change_pct"] = df["close"].pct_change() * 100
    
    # Volatility (%)
    df["volatility"] = df["close"].rolling(window=14).std() / df["close"].rolling(window=14).mean() * 100
    
    return df

def analyze_all_coins(coins=COINS):
    """
    Perform technical analysis for all cryptocurrencies
    """
    results = {}
    
    for coin in coins:
        print(f"Analyzing {coin}...")
        
        # Load data
        file_path = os.path.join(DATA_DIR, f"{coin}_data.csv")
        if not os.path.exists(file_path):
            print(f"Data file for {coin} not found")
            continue
        
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Calculate technical indicators
        df_with_indicators = calculate_technical_indicators(df)
        
        if df_with_indicators is not None:
            # Save analysis results as CSV
            output_file = os.path.join(ANALYSIS_DIR, f"{coin}_analysis.csv")
            df_with_indicators.to_csv(output_file, index=False)
            
            print(f"Analysis for {coin} saved to {output_file}")
            results[coin] = df_with_indicators
    
    return results

if __name__ == "__main__":
    # Perform technical analysis for all cryptocurrencies
    analyze_all_coins()