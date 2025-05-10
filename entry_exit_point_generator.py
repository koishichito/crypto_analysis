import pandas as pd
import numpy as np
import os
from typing import Dict, Optional, Tuple
import talib

# Import settings
from config import (
    COINS,
    DONCHIAN_PERIOD,
    ADX_PERIOD,
    ADX_THRESHOLD,
    ATR_PERIOD,
    ATR_MULTIPLIER_SL,
    ATR_MULTIPLIER_TP,
    POSITION_SIZE_PERCENT,
    LEVERAGE,
    SYMBOL,
    INTERVAL,
    PHASE_THRESHOLDS,
    PHASE_LOT_FACTOR
)

# Directory settings
STRATEGY_DIR = "strategies"
ENTRY_EXIT_DIR = "entry_exit_points"
os.makedirs(ENTRY_EXIT_DIR, exist_ok=True)

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Donchian Channels, ADX, and ATR
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added indicators
    """
    # Calculate Donchian Channels
    df['DonchianHigh'] = df['High'].rolling(window=DONCHIAN_PERIOD).max()
    df['DonchianLow'] = df['Low'].rolling(window=DONCHIAN_PERIOD).min()
    
    # Calculate ADX
    df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=ADX_PERIOD)
    
    # Calculate ATR
    df['ATR'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=ATR_PERIOD)
    
    return df

def generate_signal(df: pd.DataFrame) -> Optional[Dict]:
    """
    Generate trading signal based on Donchian breakout and ADX filter
    
    Args:
        df: DataFrame with indicators
        
    Returns:
        Dictionary with signal information or None if no signal
    """
    if df is None or df.empty:
        return None
    
    # Get latest data
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Check if ADX is above threshold
    if latest['ADX'] < ADX_THRESHOLD:
        return None
    
    # Check for Donchian breakout
    signal = None
    if latest['Close'] > latest['DonchianHigh'] and prev['Close'] <= prev['DonchianHigh']:
        signal = "BUY"
    elif latest['Close'] < latest['DonchianLow'] and prev['Close'] >= prev['DonchianLow']:
        signal = "SELL"
    
    if signal:
        return {
            'timestamp': latest['OpenTime'],
            'price': latest['Close'],
            'signal': signal,
            'atr': latest['ATR']
        }
    
    return None

def generate_trade_parameters(signal: Dict, balance: float) -> Dict:
    """
    Generate trade parameters based on signal and current balance
    
    Args:
        signal: Signal dictionary
        balance: Current account balance
        
    Returns:
        Dictionary with trade parameters
    """
    entry_price = signal['price']
    atr = signal['atr']
    
    # Calculate stop loss and take profit levels
    if signal['signal'] == "BUY":
        stop_loss = entry_price - (ATR_MULTIPLIER_SL * atr)
        take_profit = entry_price + (ATR_MULTIPLIER_TP * atr)
    else:  # SELL
        stop_loss = entry_price + (ATR_MULTIPLIER_SL * atr)
        take_profit = entry_price - (ATR_MULTIPLIER_TP * atr)
    
    # Calculate position size
    risk_amount = balance * POSITION_SIZE_PERCENT
    position_size = (risk_amount * LEVERAGE) / (abs(entry_price - stop_loss))
    
    return {
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'position_size': position_size,
        'balance': balance
    }

def get_phase(balance: float) -> Tuple[int, float]:
    """
    Determine current phase and lot factor based on balance
    
    Args:
        balance: Current account balance
        
    Returns:
        Tuple of (phase_number, lot_factor)
    """
    for i, threshold in enumerate(PHASE_THRESHOLDS, 1):
        if balance < threshold:
            return i, PHASE_LOT_FACTOR[i]
    
    return len(PHASE_THRESHOLDS), PHASE_LOT_FACTOR[len(PHASE_THRESHOLDS)]

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
    # Test the functions
    from crypto_data_collector import get_latest_data
    
    # Get latest data
    df = get_latest_data()
    if df is not None:
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Generate signal
        signal = generate_signal(df)
        if signal:
            print("\nSignal generated:")
            print(signal)
            
            # Generate trade parameters
            trade_params = generate_trade_parameters(signal, 15000)
            print("\nTrade parameters:")
            print(trade_params)
    
    # Generate entry/exit points for all cryptocurrencies
    results, points_df = generate_all_entry_exit_points()
    
    if not points_df.empty:
        # Display entry/exit points
        print("\nEntry/Exit Points Summary:")
        print(points_df[["coin", "signal", "confidence", "price", "entry_point", "exit_point", "stop_loss", "risk_reward_ratio"]])