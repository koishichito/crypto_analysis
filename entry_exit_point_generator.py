import pandas as pd
import numpy as np
import os

# Import settings
from config import COINS

# Directory settings
STRATEGY_DIR = "strategies"
ENTRY_EXIT_DIR = "entry_exit_points"
os.makedirs(ENTRY_EXIT_DIR, exist_ok=True)

def generate_entry_exit_points(df, risk_reward_ratio=5.0):
    """
    Generate entry point, exit point, and stop loss
    
    Args:
        df: DataFrame with trading signals
        risk_reward_ratio: Risk-reward ratio
        
    Returns:
        DataFrame: DataFrame with added entry/exit points
    """
    if df is None or df.empty:
        return None
    
    # Get latest price and signal
    latest = df.iloc[-1]
    price = latest["close"]
    signal = latest["composite_signal"]
    
    # Calculate entry point, exit point, and stop loss
    if signal > 0:  # Buy signal
        entry_point = price * 0.99  # 1% below current price
        stop_loss = entry_point * 0.98  # 2% below entry point
        risk = entry_point - stop_loss
        reward = risk * risk_reward_ratio
        exit_point = entry_point + reward
    elif signal < 0:  # Sell signal
        entry_point = price * 1.01  # 1% above current price
        stop_loss = entry_point * 1.02  # 2% above entry point
        risk = stop_loss - entry_point
        reward = risk * risk_reward_ratio
        exit_point = entry_point - reward
    else:  # Hold signal
        entry_point = np.nan
        exit_point = np.nan
        stop_loss = np.nan
    
    # Add results to DataFrame
    df["entry_point"] = np.nan
    df["exit_point"] = np.nan
    df["stop_loss"] = np.nan
    df.loc[df.index[-1], "entry_point"] = entry_point
    df.loc[df.index[-1], "exit_point"] = exit_point
    df.loc[df.index[-1], "stop_loss"] = stop_loss
    
    # Add risk-reward ratio
    df["risk_reward_ratio"] = np.nan
    df.loc[df.index[-1], "risk_reward_ratio"] = risk_reward_ratio if signal != 0 else np.nan
    
    return df

def generate_all_entry_exit_points(coins=COINS):
    """
    Generate entry/exit points for all cryptocurrencies
    """
    results = {}
    entry_exit_summaries = []
    
    for coin in coins:
        print(f"Generating entry/exit points for {coin}...")
        
        # Load strategy data
        file_path = os.path.join(STRATEGY_DIR, f"{coin}_strategy.csv")
        if not os.path.exists(file_path):
            print(f"Strategy file for {coin} not found")
            continue
        
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Generate entry/exit points
        df_with_points = generate_entry_exit_points(df)
        
        if df_with_points is not None:
            # Save results as CSV
            output_file = os.path.join(ENTRY_EXIT_DIR, f"{coin}_entry_exit.csv")
            df_with_points.to_csv(output_file, index=False)
            
            print(f"Entry/exit points for {coin} saved to {output_file}")
            results[coin] = df_with_points
            
            # Get latest entry/exit points
            latest = df_with_points.iloc[-1]
            
            # Create entry/exit points summary
            if not np.isnan(latest["entry_point"]):
                entry_exit_summary = {
                    "coin": coin,
                    "price": latest["close"],
                    "signal": "BUY" if latest["composite_signal"] > 0 else "SELL" if latest["composite_signal"] < 0 else "HOLD",
                    "confidence": latest["confidence"],
                    "entry_point": latest["entry_point"],
                    "exit_point": latest["exit_point"],
                    "stop_loss": latest["stop_loss"],
                    "risk_reward_ratio": latest["risk_reward_ratio"]
                }
                
                entry_exit_summaries.append(entry_exit_summary)
    
    # Convert entry/exit points summary to DataFrame
    if entry_exit_summaries:
        points_df = pd.DataFrame(entry_exit_summaries)
        
        # Sort by signal and confidence
        points_df = points_df.sort_values(by=["signal", "confidence"], ascending=[True, False])
        
        # Save summary as CSV
        summary_file = os.path.join(ENTRY_EXIT_DIR, "entry_exit_summary.csv")
        points_df.to_csv(summary_file, index=False)
        print(f"Entry/exit points summary saved to {summary_file}")
    else:
        points_df = pd.DataFrame()
        print("No entry/exit points generated")
    
    return results, points_df

if __name__ == "__main__":
    # Generate entry/exit points for all cryptocurrencies
    results, points_df = generate_all_entry_exit_points()
    
    if not points_df.empty:
        # Display entry/exit points
        print("\nEntry/Exit Points Summary:")
        print(points_df[["coin", "signal", "confidence", "price", "entry_point", "exit_point", "stop_loss", "risk_reward_ratio"]])