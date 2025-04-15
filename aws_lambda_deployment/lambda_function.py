import os
import json
import pandas as pd
import requests
from datetime import datetime
import tempfile
import boto3
from line_messaging_api import LineMessagingApi

# Get settings from environment variables
API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY")
LINE_CHANNEL_TOKEN = os.environ.get("LINE_CHANNEL_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

# Analysis target cryptocurrency list
COINS = [
    "BTC", "ETH", "BNB", "SOL", "XRP", 
    "ADA", "DOT", "AVAX", "LINK", "MATIC", 
    "DOGE", "SHIB", "UNI", "AAVE", "GRT", 
    "RNDR", "INJ", "ARB", "OP", "IMX"
]

def lambda_handler(event, context):
    """
    Lambda function handler
    """
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Collect data
            data_results = collect_data(temp_dir)
            
            # Perform technical analysis
            analysis_results = analyze_data(temp_dir, data_results)
            
            # Generate trading signals
            signals_df = generate_signals(temp_dir, analysis_results)
            
            # Calculate entry/exit points
            entry_exit_df = generate_entry_exit_points(temp_dir, signals_df)
            
            # Send LINE notification
            send_line_notification(entry_exit_df)
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Crypto analysis completed successfully",
                    "timestamp": datetime.now().isoformat()
                })
            }
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        }

def collect_data(temp_dir):
    """
    Collect cryptocurrency data
    """
    print("Collecting cryptocurrency data...")
    results = {}
    
    data_dir = os.path.join(temp_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    for coin in COINS:
        try:
            # Choose API endpoint (using 5-minute intervals)
            url = "https://min-api.cryptocompare.com/data/v2/histominute"
            
            # Set parameters
            params = {
                "fsym": coin,
                "tsym": "USD",
                "limit": 100,
                "aggregate": 5,
                "api_key": API_KEY
            }
            
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
                file_path = os.path.join(data_dir, f"{coin}_data.csv")
                df.to_csv(file_path, index=False)
                
                results[coin] = df
                print(f"  ✓ Data collected for {coin}")
            else:
                print(f"  ✗ Failed to collect data for {coin}: {data['Message']}")
        except Exception as e:
            print(f"  ✗ Exception for {coin}: {str(e)}")
    
    return results

def analyze_data(temp_dir, data_results):
    """
    Perform technical analysis
    """
    print("Performing technical analysis...")
    results = {}
    
    analysis_dir = os.path.join(temp_dir, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)
    
    # Import necessary TA libraries only once
    from ta.momentum import RSIIndicator, StochasticOscillator
    from ta.trend import MACD, SMAIndicator, EMAIndicator
    from ta.volatility import BollingerBands
    from ta.volume import OnBalanceVolumeIndicator
    
    for coin, df in data_results.items():
        try:
            # Check if required columns exist
            required_columns = ["close", "high", "low", "open", "volume"]
            if not all(col in df.columns for col in required_columns):
                print(f"  ✗ Required columns missing for {coin}")
                continue
            
            # Calculate RSI
            rsi = RSIIndicator(close=df["close"], window=14)
            df["rsi"] = rsi.rsi()
            
            # Calculate MACD
            macd = MACD(close=df["close"])
            df["macd"] = macd.macd()
            df["macd_signal"] = macd.macd_signal()
            df["macd_diff"] = macd.macd_diff()
            
            # Calculate Bollinger Bands
            bollinger = BollingerBands(close=df["close"])
            df["bb_upper"] = bollinger.bollinger_hband()
            df["bb_middle"] = bollinger.bollinger_mavg()
            df["bb_lower"] = bollinger.bollinger_lband()
            
            # Calculate Moving Averages
            df["sma_20"] = SMAIndicator(close=df["close"], window=20).sma_indicator()
            df["sma_50"] = SMAIndicator(close=df["close"], window=50).sma_indicator()
            df["ema_12"] = EMAIndicator(close=df["close"], window=12).ema_indicator()
            df["ema_26"] = EMAIndicator(close=df["close"], window=26).ema_indicator()
            
            # Calculate Stochastics
            stoch = StochasticOscillator(high=df["high"], low=df["low"], close=df["close"])
            df["stoch_k"] = stoch.stoch()
            df["stoch_d"] = stoch.stoch_signal()
            
            # Calculate OBV
            df["obv"] = OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"]).on_balance_volume()
            
            # Save analysis results
            file_path = os.path.join(analysis_dir, f"{coin}_analysis.csv")
            df.to_csv(file_path, index=False)
            
            results[coin] = df
            print(f"  ✓ Analysis completed for {coin}")
        except Exception as e:
            print(f"  ✗ Exception during analysis for {coin}: {str(e)}")
    
    return results

def generate_signals(temp_dir, analysis_results):
    """
    Generate trading signals
    """
    print("Generating trading signals...")
    signal_summaries = []
    
    strategy_dir = os.path.join(temp_dir, "strategies")
    os.makedirs(strategy_dir, exist_ok=True)
    
    for coin, df in analysis_results.items():
        try:
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
            
            # Composite signal
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
            
            # Signal strength
            df["signal_strength"] = df["composite_signal"]
            
            # Trend direction
            df["trend"] = 0
            df.loc[df["composite_signal"] >= 0.3, "trend"] = 1
            df.loc[df["composite_signal"] <= -0.3, "trend"] = -1
            
            # Confidence
            df["confidence"] = abs(df["composite_signal"]) * 100
            df["confidence"] = df["confidence"].clip(0, 100)
            
            # Save strategy
            file_path = os.path.join(strategy_dir, f"{coin}_strategy.csv")
            df.to_csv(file_path, index=False)
            
            # Get latest signal
            latest = df.iloc[-1]
            
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
            print(f"  ✓ Signals generated for {coin}")
        except Exception as e:
            print(f"  ✗ Exception during signal generation for {coin}: {str(e)}")
    
    # Create signals summary DataFrame
    signals_df = pd.DataFrame(signal_summaries)
    
    # Sort by signal and confidence
    if not signals_df.empty:
        signals_df = signals_df.sort_values(by=["signal", "confidence"], ascending=[True, False])
        
        # Save summary
        summary_file = os.path.join(strategy_dir, "trading_signals_summary.csv")
        signals_df.to_csv(summary_file, index=False)
    
    return signals_df

def generate_entry_exit_points(temp_dir, signals_df):
    """
    Generate entry/exit points
    """
    print("Generating entry/exit points...")
    entry_exit_summaries = []
    
    strategy_dir = os.path.join(temp_dir, "strategies")
    entry_exit_dir = os.path.join(temp_dir, "entry_exit_points")
    os.makedirs(entry_exit_dir, exist_ok=True)
    
    import numpy as np
    
    for _, row in signals_df.iterrows():
        coin = row["coin"]
        price = row["price"]
        signal = row["signal_strength"]
        confidence = row["confidence"]
        
        # Calculate entry point, exit point, and stop loss
        if signal > 0:  # Buy signal
            entry_point = price * 0.99  # 1% below current price
            stop_loss = entry_point * 0.98  # 2% below entry point
            risk = entry_point - stop_loss
            reward = risk * 5.0  # Risk-reward ratio of 5.0
            exit_point = entry_point + reward
        elif signal < 0:  # Sell signal
            entry_point = price * 1.01  # 1% above current price
            stop_loss = entry_point * 1.02  # 2% above entry point
            risk = stop_loss - entry_point
            reward = risk * 5.0  # Risk-reward ratio of 5.0
            exit_point = entry_point - reward
        else:  # Hold signal
            entry_point = np.nan
            exit_point = np.nan
            stop_loss = np.nan
            continue
        
        # Create entry/exit points summary
        entry_exit_summary = {
            "coin": coin,
            "price": price,
            "signal": row["signal"],
            "confidence": confidence,
            "entry_point": entry_point,
            "exit_point": exit_point,
            "stop_loss": stop_loss,
            "risk_reward_ratio": 5.0
        }
        
        entry_exit_summaries.append(entry_exit_summary)
        print(f"  ✓ Entry/exit points generated for {coin}")
    
    # Create entry/exit points summary DataFrame
    if entry_exit_summaries:
        points_df = pd.DataFrame(entry_exit_summaries)
        
        # Sort by signal and confidence
        points_df = points_df.sort_values(by=["signal", "confidence"], ascending=[True, False])
        
        # Save summary
        summary_file = os.path.join(entry_exit_dir, "entry_exit_summary.csv")
        points_df.to_csv(summary_file, index=False)
    else:
        points_df = pd.DataFrame()
    
    return points_df

def send_line_notification(entry_exit_df):
    """
    Send LINE notification
    """
    # Check if necessary environment variables are set
    if not LINE_CHANNEL_TOKEN or not LINE_USER_ID:
        print("LINE_CHANNEL_TOKEN or LINE_USER_ID not set")
        return False
    
    # Create LINE Messaging API client
    line_client = LineMessagingApi(LINE_CHANNEL_TOKEN, LINE_USER_ID)
    
    # Create summary data for notification
    summary_data = []
    for _, row in entry_exit_df.iterrows():
        summary_data.append({
            "coin": row["coin"],
            "price": row["price"],
            "signal": row["signal"],
            "confidence": row["confidence"],
            "entry_point": row["entry_point"],
            "exit_point": row["exit_point"],
            "stop_loss": row["stop_loss"]
        })
    
    # Send analysis report
    return line_client.send_analysis_report(summary_data)

if __name__ == "__main__":
    # For local testing
    test_event = {}
    test_context = {}
    lambda_handler(test_event, test_context)