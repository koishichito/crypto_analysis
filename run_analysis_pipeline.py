import os
import json
import argparse
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

from crypto_data_collector import get_latest_data
from entry_exit_point_generator import (
    calculate_indicators,
    generate_signal,
    generate_trade_parameters,
    get_phase
)
from line_messaging_api import LineMessagingApi
from config import (
    SYMBOL,
    INTERVAL,
    INITIAL_BALANCE,
    BALANCE_FILE,
    ENABLE_LINE_NOTIFY,
    LINE_CHANNEL_TOKEN,
    LINE_USER_ID
)

def load_balance() -> float:
    """
    Load current balance from file
    """
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            data = json.load(f)
            return float(data.get('balance', INITIAL_BALANCE))
    return INITIAL_BALANCE

def save_balance(balance: float):
    """
    Save current balance to file
    """
    with open(BALANCE_FILE, 'w') as f:
        json.dump({'balance': balance}, f)

def format_trade_message(symbol: str, signal: Dict, trade_params: Dict) -> str:
    """
    Format trade message for LINE notification
    """
    return f"""{symbol} {'🚀' if signal['signal'] == 'BUY' else '📉'} {signal['signal']} @{trade_params['entry_price']:.2f}
SL {trade_params['stop_loss']:.2f} / TP {trade_params['take_profit']:.2f}
Size {trade_params['position_size']:.4f} (Bal ¥{trade_params['balance']:.0f})"""

def run_analysis_pipeline(dry_run: bool = False):
    """
    Run the trading strategy pipeline
    
    Args:
        dry_run: If True, only simulate the strategy without sending notifications
    """
    print("=" * 50)
    print(f"TRADING STRATEGY PIPELINE START: {datetime.now()}")
    print("=" * 50)
    
    # Load current balance
    balance = load_balance()
    print(f"\nCurrent balance: ¥{balance:.0f}")
    
    # Get current phase
    phase, lot_factor = get_phase(balance)
    print(f"Current phase: {phase} (Lot factor: {lot_factor})")
    
    # Step 1: Get latest OHLCV data
    print("\n[STEP 1] Fetching latest OHLCV data...")
    df = get_latest_data()
    if df is None:
        print("❌ Failed to fetch data")
        return
    
    # Step 2: Calculate indicators
    print("\n[STEP 2] Calculating indicators...")
    df = calculate_indicators(df)
    
    # Step 3: Generate trading signal
    print("\n[STEP 3] Generating trading signal...")
    signal = generate_signal(df)
    
    if signal:
        print(f"\nSignal generated: {signal['signal']} @ {signal['price']:.2f}")
        
        # Step 4: Generate trade parameters
        print("\n[STEP 4] Generating trade parameters...")
        trade_params = generate_trade_parameters(signal, balance)
        
        # Apply lot factor
        trade_params['position_size'] *= lot_factor
        
        # Format message
        message = format_trade_message(SYMBOL, signal, trade_params)
        print(f"\nTrade message:\n{message}")
        
        # Step 5: Send LINE notification
        if not dry_run and ENABLE_LINE_NOTIFY:
            print("\n[STEP 5] Sending LINE notification...")
            try:
                line_client = LineMessagingApi(LINE_CHANNEL_TOKEN, LINE_USER_ID)
                result = line_client.send_message(message)
                
                if result:
                    print("✅ LINE notification sent successfully!")
                else:
                    print("❌ Failed to send LINE notification")
            except Exception as e:
                print(f"❌ Error sending LINE notification: {str(e)}")
    else:
        print("\nNo trading signal generated")
    
    print("\n" + "=" * 50)
    print(f"TRADING STRATEGY PIPELINE COMPLETE: {datetime.now()}")
    print("=" * 50)

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Cryptocurrency Trading Strategy")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run in simulation mode without sending notifications")
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Run the trading strategy pipeline
    run_analysis_pipeline(args.dry_run)