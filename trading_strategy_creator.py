import pandas as pd
import numpy as np
import os

# Import settings
from config import COINS

# Directory settings
ANALYSIS_DIR = "analysis"
STRATEGY_DIR = "strategies"
os.makedirs(STRATEGY_DIR, exist_ok=True)

def generate_trading_signals(df):
    """
    Generate trading signals
    
    Args:
        df: DataFrame with technical indicators
        
    Returns:
        DataFrame: DataFrame with added trading signals
    """
    if df is None or df.empty:
        return None
    
    # RSI signal
    df["rsi_signal"] = 0
    df.loc[df["rsi"] < 30, "rsi_signal"] = 1  # Buy signal
    df.loc[df["rsi"] > 70, "rsi_signal"] = -1  # Sell signal
    
    # MACD cross signal
    df["macd_cross_signal"] = 0
    df.loc[(df["macd"] > df["macd_signal"]) & (df["macd"].shift(1) <= df["macd_signal"].shift(1)), "macd_cross_signal"] = 1  # Buy signal
    df.loc[(df["macd"] < df["macd_signal"]) & (df["macd"].shift(1) >= df["macd_signal"].shift(1)), "macd_cross_signal"] = -1  # Sell signal
    
    # Bollinger Bands signal
    df["bb_signal"] = 0
    df.loc[df["close"] < df["bb_lower"], "bb_signal"] = 1  # Buy signal
    df.loc[df["close"] > df["bb_upper"], "bb_signal"] = -1  # Sell signal
    
    # Moving average cross signal
    df["ma_cross_signal"] = 0
    df.loc[(df["sma_20"] > df["sma_50"]) & (df["sma_20"].shift(1) <= df["sma_50"].shift(1)), "ma_cross_signal"] = 1  # Buy signal
    df.loc[(df["sma_20"] < df["sma_50"]) & (df["sma_20"].shift(1) >= df["sma_50"].shift(1)), "ma_cross_signal"] = -1  # Sell signal
    
    # Stochastics signal
    df["stoch_signal"] = 0
    df.loc[(df["stoch_k"] < 20) & (df["stoch_d"] < 20) & (df["stoch_k"] > df["stoch_d"]), "stoch_signal"] = 1  # Buy signal
    df.loc[(df["stoch_k"] > 80) & (df["stoch_d"] > 80) & (df["stoch_k"] < df["stoch_d"]), "stoch_signal"] = -1  # Sell signal
    
    # Composite signal (weighted sum of individual signals)
    weights = {
        "rsi_signal": 0.2,
        "macd_cross_signal": 0.3,
        "bb_signal": 0.15,
        "ma_cross_signal": 0.25,
        "stoch_signal": 0.1
    }
    
    df["composite_signal"] = (
        df["rsi_signal"] * weights["rsi_signal"] +
        df["macd_cross_signal"] * weights["macd_cross_signal"] +
        df["bb_signal"] * weights["bb_signal"] +
        df["ma_cross_signal"] * weights["ma_cross_signal"] +
        df["stoch_signal"] * weights["stoch_signal"]
    )
    
    # Signal strength (-1.0 to 1.0 range)
    df["signal_strength"] = df["composite_signal"]
    
    # Trend direction (1: uptrend, 0: neutral, -1: downtrend)
    df["trend"] = 0
    df.loc[df["composite_signal"] >= 0.3, "trend"] = 1
    df.loc[df["composite_signal"] <= -0.3, "trend"] = -1
    
    # Confidence (0-100%)
    df["confidence"] = abs(df["composite_signal"]) * 100
    df["confidence"] = df["confidence"].clip(0, 100)
    
    return df

def create_trading_strategies(coins=COINS):
    """
    Create trading strategies for all cryptocurrencies
    """
    results = {}
    signal_summaries = []
    
    for coin in coins:
        print(f"Creating trading strategy for {coin}...")
        
        # Load analysis data
        file_path = os.path.join(ANALYSIS_DIR, f"{coin}_analysis.csv")
        if not os.path.exists(file_path):
            print(f"Analysis file for {coin} not found")
            continue
        
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Generate trading signals
        df_with_signals = generate_trading_signals(df)
        
        if df_with_signals is not None:
            # Save strategy as CSV
            output_file = os.path.join(STRATEGY_DIR, f"{coin}_strategy.csv")
            df_with_signals.to_csv(output_file, index=False)
            
            print(f"Trading strategy for {coin} saved to {output_file}")
            results[coin] = df_with_signals
            
            # Get latest signal
            latest = df_with_signals.iloc[-1]
            
            # Create signal summary
            signal_summary = {
                "coin": coin,
                "price": latest["close"],
                "signal": "BUY" if latest["composite_signal"] > 0 else "SELL" if latest["composite_signal"] < 0 else "HOLD",
                "signal_strength": latest["composite_signal"],
                "confidence": latest["confidence"],
                "rsi": latest["rsi"],
                "trend": "UPTREND" if latest["trend"] == 1 else "DOWNTREND" if latest["trend"] == -1 else "NEUTRAL"
            }
            
            signal_summaries.append(signal_summary)
    
    # Convert signal summaries to DataFrame
    signals_df = pd.DataFrame(signal_summaries)
    
    # Sort by signal and confidence
    signals_df = signals_df.sort_values(by=["signal", "confidence"], ascending=[True, False])
    
    # Save signal summary as CSV
    summary_file = os.path.join(STRATEGY_DIR, "trading_signals_summary.csv")
    signals_df.to_csv(summary_file, index=False)
    print(f"Trading signals summary saved to {summary_file}")
    
    return results, signals_df

if __name__ == "__main__":
    # Create trading strategies for all cryptocurrencies
    results, signals_df = create_trading_strategies()
    
    # Display trading signals
    print("\nTrading Signals Summary:")
    print(signals_df[["coin", "signal", "confidence", "price", "rsi", "trend"]])