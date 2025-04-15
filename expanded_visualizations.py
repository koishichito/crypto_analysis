import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Import settings
from config import COINS

# Directory settings
VISUALIZATION_DIR = "visualizations"
os.makedirs(VISUALIZATION_DIR, exist_ok=True)

def create_price_chart(df, coin, save_path=None):
    """
    Create price chart with technical indicators
    
    Args:
        df: DataFrame with price data and technical indicators
        coin: Cryptocurrency symbol
        save_path: Path to save the chart (if None, will show instead)
    """
    plt.figure(figsize=(14, 10))
    
    # Create subplot grid
    gs = plt.GridSpec(4, 1, height_ratios=[3, 1, 1, 1])
    
    # Price and indicators chart
    ax1 = plt.subplot(gs[0])
    ax1.plot(df['timestamp'], df['close'], label='Close Price', color='blue')
    ax1.plot(df['timestamp'], df['sma_20'], label='SMA 20', color='orange', alpha=0.7)
    ax1.plot(df['timestamp'], df['sma_50'], label='SMA 50', color='red', alpha=0.7)
    ax1.plot(df['timestamp'], df['bb_upper'], label='Bollinger Upper', color='green', linestyle='--', alpha=0.4)
    ax1.plot(df['timestamp'], df['bb_middle'], label='Bollinger Middle', color='green', linestyle='-', alpha=0.4)
    ax1.plot(df['timestamp'], df['bb_lower'], label='Bollinger Lower', color='green', linestyle='--', alpha=0.4)
    
    # Highlight buy/sell signals if available
    if 'composite_signal' in df.columns:
        buy_signals = df[df['composite_signal'] > 0]
        sell_signals = df[df['composite_signal'] < 0]
        
        ax1.scatter(buy_signals['timestamp'], buy_signals['close'], color='green', 
                   marker='^', s=100, label='Buy Signal')
        ax1.scatter(sell_signals['timestamp'], sell_signals['close'], color='red', 
                   marker='v', s=100, label='Sell Signal')
    
    ax1.set_title(f'{coin}/USD Price Chart with Indicators', fontsize=15)
    ax1.set_ylabel('Price (USD)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    
    # Volume chart
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ax2.bar(df['timestamp'], df['volume'], color='blue', alpha=0.5, width=0.8)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # RSI chart
    ax3 = plt.subplot(gs[2], sharex=ax1)
    ax3.plot(df['timestamp'], df['rsi'], color='purple')
    ax3.axhline(70, color='red', linestyle='--', alpha=0.5)
    ax3.axhline(30, color='green', linestyle='--', alpha=0.5)
    ax3.set_ylabel('RSI', fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # MACD chart
    ax4 = plt.subplot(gs[3], sharex=ax1)
    ax4.plot(df['timestamp'], df['macd'], color='blue', label='MACD')
    ax4.plot(df['timestamp'], df['macd_signal'], color='red', label='Signal')
    ax4.bar(df['timestamp'], df['macd_diff'], color=np.where(df['macd_diff'] > 0, 'green', 'red'), alpha=0.5, width=0.8)
    ax4.set_ylabel('MACD', fontsize=12)
    ax4.set_xlabel('Date', fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper left')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    else:
        plt.show()
        return None

def create_signal_distribution_chart(signals_df, save_path=None):
    """
    Create a pie chart showing the distribution of trading signals
    
    Args:
        signals_df: DataFrame with trading signals
        save_path: Path to save the chart (if None, will show instead)
    """
    plt.figure(figsize=(10, 7))
    
    # Count signals
    signal_counts = signals_df['signal'].value_counts()
    
    # Create pie chart
    colors = ['#2ecc71', '#e74c3c', '#3498db']  # Green (Buy), Red (Sell), Blue (Hold)
    explode = (0.1, 0.1, 0) if len(signal_counts) >= 3 else None  # Emphasize Buy and Sell
    
    plt.pie(signal_counts, labels=signal_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=colors, explode=explode, shadow=True)
    plt.axis('equal')  # Keep the pie as a circle
    
    plt.title('Cryptocurrency Trading Signal Distribution', fontsize=16)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    else:
        plt.show()
        return None

def create_confidence_ranking_chart(signals_df, signal_type="BUY", top_n=10, save_path=None):
    """
    Create a bar chart showing the confidence ranking for a specific signal type
    
    Args:
        signals_df: DataFrame with trading signals
        signal_type: Type of signal to rank ("BUY", "SELL", or "HOLD")
        top_n: Number of cryptocurrencies to show
        save_path: Path to save the chart (if None, will show instead)
    """
    # Filter by signal type
    filtered_df = signals_df[signals_df['signal'] == signal_type]
    
    if filtered_df.empty:
        print(f"No {signal_type} signals found")
        return None
    
    # Sort by confidence and take top N
    top_df = filtered_df.sort_values('confidence', ascending=False).head(top_n)
    
    plt.figure(figsize=(12, 8))
    
    # Create bar chart
    colors = {'BUY': 'green', 'SELL': 'red', 'HOLD': 'blue'}
    bars = plt.barh(top_df['coin'], top_df['confidence'], color=colors[signal_type], alpha=0.7)
    
    # Add labels
    for i, (confidence, price) in enumerate(zip(top_df['confidence'], top_df['price'])):
        plt.text(confidence + 1, i, f"${price:.4f}", va='center')
    
    plt.xlabel('Confidence (%)', fontsize=12)
    plt.ylabel('Cryptocurrency', fontsize=12)
    plt.title(f'Top {top_n} {signal_type} Signals by Confidence', fontsize=16)
    plt.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    else:
        plt.show()
        return None

def create_visualization_for_all_coins(analysis_dir="analysis", signal_summary=None):
    """
    Create visualizations for all cryptocurrencies
    
    Args:
        analysis_dir: Directory containing analysis results
        signal_summary: DataFrame with signal summary (if None, will try to load from file)
    """
    print("Creating visualizations for all cryptocurrencies...")
    
    charts_created = []
    
    # Create directory for individual charts
    coin_charts_dir = os.path.join(VISUALIZATION_DIR, "coin_charts")
    os.makedirs(coin_charts_dir, exist_ok=True)
    
    # Process each coin
    for coin in COINS:
        analysis_file = os.path.join(analysis_dir, f"{coin}_analysis.csv")
        if os.path.exists(analysis_file):
            df = pd.read_csv(analysis_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create price chart
            chart_path = os.path.join(coin_charts_dir, f"{coin}_chart.png")
            create_price_chart(df, coin, chart_path)
            charts_created.append(chart_path)
            print(f"  ✓ Chart created for {coin}")
        else:
            print(f"  ✗ Analysis file for {coin} not found")
    
    # Load signal summary if not provided
    if signal_summary is None:
        summary_file = os.path.join("batch_processing", "trading_signals_summary.csv")
        if os.path.exists(summary_file):
            signal_summary = pd.read_csv(summary_file)
    
    # Create signal distribution chart if we have signal summary
    if signal_summary is not None and not signal_summary.empty:
        dist_chart_path = os.path.join(VISUALIZATION_DIR, "signal_distribution.png")
        create_signal_distribution_chart(signal_summary, dist_chart_path)
        charts_created.append(dist_chart_path)
        print(f"  ✓ Signal distribution chart created")
        
        # Create confidence ranking charts for BUY and SELL signals
        buy_chart_path = os.path.join(VISUALIZATION_DIR, "buy_confidence_ranking.png")
        create_confidence_ranking_chart(signal_summary, "BUY", 10, buy_chart_path)
        charts_created.append(buy_chart_path)
        print(f"  ✓ BUY confidence ranking chart created")
        
        sell_chart_path = os.path.join(VISUALIZATION_DIR, "sell_confidence_ranking.png")
        create_confidence_ranking_chart(signal_summary, "SELL", 10, sell_chart_path)
        charts_created.append(sell_chart_path)
        print(f"  ✓ SELL confidence ranking chart created")
    
    print(f"Visualization complete. {len(charts_created)} charts created.")
    return charts_created

if __name__ == "__main__":
    # Create visualizations for all coins
    create_visualization_for_all_coins()