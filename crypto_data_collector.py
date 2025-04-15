import requests
import pandas as pd
import os
from datetime import datetime
import time

# Import API key and coin list from config
from config import API_KEY, COINS

# Data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_crypto_data(coin, limit=100, interval="5m"):
    """
    Fetch cryptocurrency data from CryptoCompare API
    
    Args:
        coin: Cryptocurrency symbol (e.g., BTC)
        limit: Number of data points to retrieve
        interval: Time interval (1m, 5m, 15m, 30m, 1h, 1d)
        
    Returns:
        DataFrame: Retrieved data
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
            file_path = os.path.join(DATA_DIR, f"{coin}_data.csv")
            df.to_csv(file_path, index=False)
            
            print(f"Data for {coin} saved to {file_path}")
            return df
        else:
            print(f"Error fetching data for {coin}: {data['Message']}")
            return None
    except Exception as e:
        print(f"Exception when fetching data for {coin}: {str(e)}")
        return None

def collect_all_data(coins=COINS, interval="5m", limit=100):
    """
    Collect data for all cryptocurrencies
    """
    results = {}
    for coin in coins:
        print(f"Collecting data for {coin}...")
        df = fetch_crypto_data(coin, limit, interval)
        if df is not None:
            results[coin] = df
        # Short delay to avoid API rate limits
        time.sleep(0.5)
    
    return results

if __name__ == "__main__":
    # Collect data for all cryptocurrencies
    collect_all_data()