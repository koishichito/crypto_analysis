# config.py
import os

# API settings (replace with your actual API keys)
API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "396e378fa288213268864e6dea987ae0d76c2584dc2ef69ca201026befea5633")
LINE_CHANNEL_TOKEN = os.getenv("LINE_CHANNEL_TOKEN", "dD1USw0IRnGPm+vie3RmyJwAHCgXwZ6rV5g6tUp8+EO7VvXvhiQ//O8VRcNZQKvOzXQEF+PHanRYnPraoUJhwDuuE9NcL945zEr7HkObCPOT2ZQj6i7c+08sjOkVXCnnz4zbTV7gH+7+kbRVrkXj+wdB04t89/1O/w1cDnyilFU=")
LINE_USER_ID        = os.getenv("LINE_USER_ID",        "Ue8667982a0de0cc4542d4aa97dec9cdf")

# Analysis target cryptocurrency list
COINS = [
    "BTC", "ETH", "BNB", "SOL", "XRP",
    "ADA", "DOT", "AVAX", "LINK", "MATIC",
    "DOGE", "SHIB", "UNI", "AAVE", "GRT",
    "RNDR", "INJ", "ARB", "OP", "IMX"
]