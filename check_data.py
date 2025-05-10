import pandas as pd

# BTCUSDTのデータを読み込む
btc_data = pd.read_csv('data/BTCUSDT_data.csv')

# 最初の5行を表示
print("BTCUSDT Data:")
print(btc_data.head())

# 基本的な統計情報を表示
print("\nBTCUSDT Basic Statistics:")
print(btc_data.describe()) 