import os
import time
import concurrent.futures
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import json

# Import settings
from config import API_KEY, COINS

# Directory settings
BATCH_DIR = "batch_processing"
os.makedirs(BATCH_DIR, exist_ok=True)
os.makedirs(os.path.join(BATCH_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(BATCH_DIR, "analysis"), exist_ok=True)
os.makedirs(os.path.join(BATCH_DIR, "visualizations"), exist_ok=True)

def fetch_crypto_data_batch(coin, limit=100, interval="5m"):
    """
    Fetch cryptocurrency data from CryptoCompare API (for batch processing)
    """
    # Choose API endpoint based on interval
    if interval in ["1m", "5m", "15m", "30m"]:
        url = "https://min-api.cryptocompare.com/data/v2/histominute"
        if interval == "1m":
            aggregate = 1
        elif interval == "5m":
            aggregate = 5
        elif interval == "15m":
            aggregate = 15
        else:  # 30m
            aggregate = 30
    elif interval == "1h":
        url = "https://min-api.cryptocompare.com/data/v2/histohour"
        aggregate = 1
    else:  # 1d
        url = "https://min-api.cryptocompare.com/data/v2/histoday"
        aggregate = 1
    
    # Set parameters
    params = {
        "fsym": coin,
        "tsym": "USD",
        "limit": limit,
        "aggregate": aggregate,
        "api_key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["Response"] == "Success":
            df = pd.DataFrame(data["Data"]["Data"])
            
            # Convert timestamp to datetime
            df["time"] = pd.to_datetime(df["time"], unit="s")
            
            # Rename columns
            df = df.rename(columns={
                "time": "timestamp",
                "volumefrom": "volume"
            })
            
            # Save data as CSV
            file_path = os.path.join(BATCH_DIR, "data", f"{coin}_data.csv")
            df.to_csv(file_path, index=False)
            
            return df, coin
        else:
            print(f"Error fetching data for {coin}: {data['Message']}")
            return None, coin
    except Exception as e:
        print(f"Exception when fetching data for {coin}: {str(e)}")
        return None, coin

def calculate_technical_indicators_batch(data_tuple):
    """
    Calculate technical indicators (for batch processing)
    """
    df, coin = data_tuple
    
    if df is None or df.empty:
        return None, coin
    
    # Similar to the calculate_technical_indicators function in technical_indicator_analyzer.py
    # Calculate RSI
    from ta.momentum import RSIIndicator
    rsi = RSIIndicator(close=df["close"], window=14)
    df["rsi"] = rsi.rsi()
    
    # Calculate MACD
    from ta.trend import MACD
    macd = MACD(close=df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()
    
    # Calculate Bollinger Bands
    from ta.volatility import BollingerBands
    bollinger = BollingerBands(close=df["close"])
    df["bb_upper"] = bollinger.bollinger_hband()
    df["bb_middle"] = bollinger.bollinger_mavg()
    df["bb_lower"] = bollinger.bollinger_lband()
    
    # Calculate Moving Averages
    from ta.trend import SMAIndicator, EMAIndicator
    df["sma_20"] = SMAIndicator(close=df["close"], window=20).sma_indicator()
    df["sma_50"] = SMAIndicator(close=df["close"], window=50).sma_indicator()
    df["ema_12"] = EMAIndicator(close=df["close"], window=12).ema_indicator()
    df["ema_26"] = EMAIndicator(close=df["close"], window=26).ema_indicator()
    
    # Save analysis results
    file_path = os.path.join(BATCH_DIR, "analysis", f"{coin}_analysis.csv")
    df.to_csv(file_path, index=False)
    
    return df, coin

def generate_trading_signals_batch(data_tuple):
    """
    Generate trading signals (for batch processing)
    """
    df, coin = data_tuple
    
    if df is None or df.empty:
        return None, coin, None
    
    # Generate trading signals (simplified version)
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
    
    # Composite signal (weighted sum of individual signals)
    weights = {
        "rsi_signal": 0.3,
        "macd_cross_signal": 0.4,
        "bb_signal": 0.3
    }
    
    df["composite_signal"] = (
        df["rsi_signal"] * weights["rsi_signal"] +
        df["macd_cross_signal"] * weights["macd_cross_signal"] +
        df["bb_signal"] * weights["bb_signal"]
    )
    
    # Get latest values for summary
    latest = df.iloc[-1]
    signal_summary = {
        "coin": coin,
        "price": latest["close"],
        "signal": "BUY" if latest["composite_signal"] > 0 else "SELL" if latest["composite_signal"] < 0 else "HOLD",
        "confidence": abs(latest["composite_signal"]) * 100,
        "rsi": latest["rsi"],
        "trend": "UPTREND" if latest["sma_20"] > latest["sma_50"] else "DOWNTREND"
    }
    
    return df, coin, signal_summary

def batch_process_cryptocurrencies(coins=COINS, interval="5m", limit=100, max_workers=5):
    """
    Execute batch processing for cryptocurrencies
    """
    start_time = time.time()
    print(f"Starting batch processing for {len(coins)} cryptocurrencies...")
    
    # 1. Data collection (parallel processing)
    print("\n1. Collecting data in parallel...")
    data_collection_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_coin = {executor.submit(fetch_crypto_data_batch, coin, limit, interval): coin for coin in coins}
        
        data_results = {}
        for future in concurrent.futures.as_completed(future_to_coin):
            coin = future_to_coin[future]
            try:
                df, coin_name = future.result()
                if df is not None:
                    data_results[coin_name] = df
                    print(f"  ✓ Data collected for {coin_name}")
                else:
                    print(f"  ✗ Failed to collect data for {coin_name}")
            except Exception as e:
                print(f"  ✗ Exception for {coin}: {str(e)}")
    
    data_collection_time = time.time() - data_collection_start
    print(f"Data collection completed in {data_collection_time:.2f} seconds")
    
    # 2. Technical indicator calculation (parallel processing)
    print("\n2. Calculating technical indicators in parallel...")
    analysis_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        analysis_futures = [executor.submit(calculate_technical_indicators_batch, (data_results[coin], coin)) 
                           for coin in data_results]
        
        analysis_results = {}
        for future in concurrent.futures.as_completed(analysis_futures):
            try:
                df, coin = future.result()
                if df is not None:
                    analysis_results[coin] = df
                    print(f"  ✓ Analysis completed for {coin}")
                else:
                    print(f"  ✗ Failed to analyze {coin}")
            except Exception as e:
                print(f"  ✗ Exception during analysis: {str(e)}")
    
    analysis_time = time.time() - analysis_start
    print(f"Technical analysis completed in {analysis_time:.2f} seconds")
    
    # 3. Trading signal generation (parallel processing)
    print("\n3. Generating trading signals in parallel...")
    signals_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        signal_futures = [executor.submit(generate_trading_signals_batch, (analysis_results[coin], coin)) 
                         for coin in analysis_results]
        
        signal_results = {}
        signal_summaries = []
        
        for future in concurrent.futures.as_completed(signal_futures):
            try:
                df, coin, signal_summary = future.result()
                if df is not None:
                    signal_results[coin] = df
                    if signal_summary:
                        signal_summaries.append(signal_summary)
                    print(f"  ✓ Signals generated for {coin}")
                else:
                    print(f"  ✗ Failed to generate signals for {coin}")
            except Exception as e:
                print(f"  ✗ Exception during signal generation: {str(e)}")
    
    signals_time = time.time() - signals_start
    print(f"Signal generation completed in {signals_time:.2f} seconds")
    
    # Create signals summary DataFrame
    signals_df = pd.DataFrame(signal_summaries)
    
    # Sort by signal and confidence
    if not signals_df.empty:
        signals_df = signals_df.sort_values(by=["signal", "confidence"], ascending=[True, False])
        
        # Save summary
        summary_file = os.path.join(BATCH_DIR, "trading_signals_summary.csv")
        signals_df.to_csv(summary_file, index=False)
        print(f"\nTrading signals summary saved to {summary_file}")
    
    total_time = time.time() - start_time
    print(f"\nBatch processing completed in {total_time:.2f} seconds")
    
    return signal_results, signals_df

if __name__ == "__main__":
    # Execute batch processing
    results, signals_df = batch_process_cryptocurrencies(COINS)
    
    # Display trading signals
    if not signals_df.empty:
        print("\nTrading Signals Summary:")
        print(signals_df[["coin", "signal", "confidence", "price", "rsi", "trend"]])