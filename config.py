# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Binance API settings
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "1CK3M5agDU33u8hZAw3cQUt34FVRVjFIoz6poWOC8GwJqvAWh21Lm4GxWW6fzzd9")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "F0Cm86UFSWAkemXympySsoscCjak486bX4dtda0IfewTxH2p9Y6qNl3YcLc4bW2h")

# LINE Notify settings
LINE_CHANNEL_TOKEN = os.getenv("LINE_CHANNEL_TOKEN", "dD1USw0IRnGPm+vie3RmyJwAHCgXwZ6rV5g6tUp8+EO7VvXvhiQ//O8VRcNZQKvOzXQEF+PHanRYnPraoUJhwDuuE9NcL945zEr7HkObCPOT2ZQj6i7c+08sjOkVXCnnz4zbTV7gH+7+kbRVrkXj+wdB04t89/1O/w1cDnyilFU=")
LINE_USER_ID = os.getenv("LINE_USER_ID", "Ue8667982a0de0cc4542d4aa97dec9cdf")
ENABLE_LINE_NOTIFY = os.getenv("ENABLE_LINE_NOTIFY", "True").lower() == "true"

# Trading parameters
SYMBOL = "BTCUSDT"
INTERVAL = "1h"
LEVERAGE = 10
INITIAL_BALANCE = 15000  # JPY

# Strategy parameters
DONCHIAN_PERIOD = 20
ADX_PERIOD = 14
ADX_THRESHOLD = 25
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 1.5
ATR_MULTIPLIER_TP = 3.0
POSITION_SIZE_PERCENT = 0.04

# Phase management
PHASE_THRESHOLDS = [25000, 40000, 50000]  # JPY
PHASE_LOT_FACTOR = {1: 1.0, 2: 1.0, 3: 1.0}

# File paths
DATA_DIR = "data"
BALANCE_FILE = "balance.json"
LOG_DIR = "logs"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Analysis target cryptocurrency list
COINS = [
    "BTC", "ETH", "BNB", "SOL", "XRP",
    "ADA", "DOT", "AVAX", "LINK", "MATIC",
    "DOGE", "SHIB", "UNI", "AAVE", "GRT",
    "RNDR", "INJ", "ARB", "OP", "IMX"
]