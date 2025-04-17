import os
import argparse
import pandas as pd
from datetime import datetime

# Import all necessary modules
from crypto_data_collector import collect_all_data
from technical_indicator_analyzer import analyze_all_coins
from trading_strategy_creator import create_trading_strategies
from entry_exit_point_generator import generate_all_entry_exit_points
from expanded_visualizations import create_visualization_for_all_coins
from config import COINS, LINE_CHANNEL_TOKEN, LINE_USER_ID
from line_messaging_api import LineMessagingApi

def run_analysis_pipeline(interval="5m", limit=100, send_line_notification=True):
    """
    Run the complete cryptocurrency analysis pipeline
    
    Args:
        interval: Time interval for data collection (1m, 5m, 15m, 30m, 1h, 1d)
        limit: Number of data points to retrieve
        send_line_notification: Whether to send results to LINE
    """
    print("=" * 50)
    print(f"CRYPTOCURRENCY ANALYSIS PIPELINE START: {datetime.now()}")
    print("=" * 50)
    
    # Step 1: Collect cryptocurrency data
    print("\n[STEP 1] Collecting cryptocurrency data...")
    data_results = collect_all_data(COINS, interval, limit)
    print(f"Data collection completed for {len(data_results)} cryptocurrencies.")
    
    # Step 2: Perform technical analysis
    print("\n[STEP 2] Performing technical analysis...")
    analysis_results = analyze_all_coins(COINS)
    print(f"Technical analysis completed for {len(analysis_results)} cryptocurrencies.")
    
    # Step 3: Generate trading signals
    print("\n[STEP 3] Generating trading signals...")
    strategy_results, signals_df = create_trading_strategies(COINS)
    print(f"Trading signals generated for {len(strategy_results)} cryptocurrencies.")
    
    # Display trading signals summary
    if not signals_df.empty:
        print("\nTrading Signals Summary:")
        print(signals_df[["coin", "signal", "confidence", "price", "rsi", "trend"]])
        
        # Count signals by type
        signal_counts = signals_df["signal"].value_counts()
        buy_count = signal_counts.get("BUY", 0)
        sell_count = signal_counts.get("SELL", 0)
        hold_count = signal_counts.get("HOLD", 0)
        
        print(f"\nSignal Distribution: BUY: {buy_count}, SELL: {sell_count}, HOLD: {hold_count}")
        
        # Determine market trend
        if buy_count > sell_count:
            market_trend = "BULLISH (Uptrend)"
        elif sell_count > buy_count:
            market_trend = "BEARISH (Downtrend)"
        else:
            market_trend = "NEUTRAL (Sideways)"
            
        print(f"Overall Market Trend: {market_trend}")
    
    # Step 4: Generate entry/exit points
    print("\n[STEP 4] Generating entry/exit points...")
    points_results, points_df = generate_all_entry_exit_points(COINS)
    
    if not points_df.empty:
        print("\nEntry/Exit Points Summary:")
        print(points_df[["coin", "signal", "confidence", "price", "entry_point", "exit_point", "stop_loss"]])
    
    # Step 5: Create visualizations
    print("\n[STEP 5] Creating visualizations...")
    charts_created = create_visualization_for_all_coins("analysis", signals_df)
    print(f"Created {len(charts_created)} visualization charts.")
    
    # Step 6: Send LINE notification with results
    if send_line_notification and not points_df.empty:
        print("\n[STEP 6] Sending LINE notification...")
        try:
            # Prepare summary data for LINE notification
            summary_data = []
            for _, row in points_df.iterrows():
                summary_data.append({
                    "coin": row["coin"],
                    "signal": row["signal"],
                    "confidence": row["confidence"],
                    "price": row["price"],
                    "entry_point": row["entry_point"],
                    "exit_point": row["exit_point"]
                })
            
            # Initialize LINE client
            line_client = LineMessagingApi(LINE_CHANNEL_TOKEN, LINE_USER_ID)
            
            # Send analysis report
            result = line_client.send_analysis_report(summary_data)
            
            if result:
                print("✅ LINE notification sent successfully!")
            else:
                print("❌ Failed to send LINE notification. Check credentials.")
        except Exception as e:
            print(f"❌ Error sending LINE notification: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"CRYPTOCURRENCY ANALYSIS PIPELINE COMPLETE: {datetime.now()}")
    print("=" * 50)
    
    return {
        "data_results": data_results,
        "analysis_results": analysis_results,
        "strategy_results": strategy_results,
        "signals_df": signals_df,
        "points_results": points_results,
        "points_df": points_df,
        "charts_created": charts_created
    }

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Cryptocurrency Technical Analysis Tool")
    
    parser.add_argument("--interval", type=str, default="5m",
                        choices=["1m", "5m", "15m", "30m", "1h", "1d"],
                        help="Time interval for data collection")
    
    parser.add_argument("--limit", type=int, default=100,
                        help="Number of data points to retrieve")
    
    parser.add_argument("--no-line", action="store_true",
                        help="Disable LINE notification")
    
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Run the complete analysis pipeline
    results = run_analysis_pipeline(args.interval, args.limit, not args.no_line)