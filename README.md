# Cryptocurrency Technical Analysis Tool

This project provides a comprehensive cryptocurrency technical analysis system for collecting data, analyzing trends, generating trading signals, and visualizing cryptocurrency market conditions.

## Project Structure

```
crypto_analysis/
├── data/                       # Collected cryptocurrency data
├── analysis/                   # Technical analysis results
├── visualizations/             # Charts and data visualizations
├── aws_lambda_deployment/      # AWS Lambda deployment files
├── config.py                   # Configuration settings
├── crypto_data_collector.py    # Cryptocurrency data collection
├── technical_indicator_analyzer.py  # Technical indicator calculations
├── trading_strategy_creator.py # Trading signal generator
├── entry_exit_point_generator.py    # Entry/exit point calculator
├── expanded_visualizations.py  # Chart and visualization creator
├── batch_processor.py          # Parallel processing module
├── run_analysis_pipeline.py    # Main orchestrator
└── requirements.txt            # Python dependencies
```

## Features

- **Data Collection**: Retrieve historical price data for multiple cryptocurrencies
- **Technical Analysis**: Calculate various technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **Trading Signals**: Generate buy/sell signals based on technical indicators
- **Entry/Exit Points**: Calculate optimal entry points, exit targets, and stop-loss levels
- **Visualizations**: Create charts and visual aids for analysis
- **Batch Processing**: Process multiple cryptocurrencies in parallel
- **LINE Notifications**: Send trading signals via LINE Messaging API
- **AWS Lambda Deployment**: Deploy the system to AWS Lambda for automated analysis

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd crypto_analysis
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Set up your API keys in `config.py`:
```python
API_KEY = "YOUR_CRYPTOCOMPARE_API_KEY"
LINE_CHANNEL_TOKEN = "YOUR_LINE_MESSAGING_API_CHANNEL_ACCESS_TOKEN"
LINE_USER_ID = "YOUR_LINE_USER_ID"
```

## Usage

### Running the Complete Analysis Pipeline

To run the complete analysis pipeline:

```
python run_analysis_pipeline.py
```

This will:
1. Collect cryptocurrency data
2. Perform technical analysis
3. Generate trading signals
4. Calculate entry/exit points
5. Create visualizations

### Command-line Options

You can customize the analysis with the following options:

```
python run_analysis_pipeline.py --interval 5m --limit 100
```

- `--interval`: Time interval for data (1m, 5m, 15m, 30m, 1h, 1d)
- `--limit`: Number of data points to retrieve

### Running Individual Modules

You can also run individual modules separately:

```
# Collect data only
python crypto_data_collector.py

# Perform technical analysis
python technical_indicator_analyzer.py

# Generate trading signals
python trading_strategy_creator.py

# Calculate entry/exit points
python entry_exit_point_generator.py

# Create visualizations
python expanded_visualizations.py

# Run batch processing
python batch_processor.py
```

## AWS Lambda Deployment

To deploy the system to AWS Lambda:

1. Install AWS CLI and configure it with your credentials
2. Package the Lambda deployment files:
```
cd aws_lambda_deployment
pip install -r requirements.txt -t .
zip -r lambda_deployment.zip .
```

3. Create a new Lambda function in AWS Console
4. Upload the `lambda_deployment.zip` package
5. Set environment variables in the Lambda configuration:
   - `CRYPTOCOMPARE_API_KEY`
   - `LINE_CHANNEL_TOKEN`
   - `LINE_USER_ID`

6. Set up a CloudWatch Events trigger to run the analysis on a schedule

## LINE Notifications

To receive trading signals via LINE:

1. Create a LINE Bot in the LINE Developers Console
2. Get your Channel Access Token
3. Add your bot as a friend and get your User ID
4. Update `config.py` with these values

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Cryptocurrency Trading Strategy

This project implements an automated trading strategy for Binance Futures (BTCUSDT) using Donchian Channels, ADX, and ATR for risk management.

## Strategy Overview

The strategy combines:
- Donchian Channel breakout signals
- ADX trend filter
- ATR-based risk management
- 10x leverage with compound position sizing
- Phase-based lot size adjustment

### Key Components

1. **Entry Signals**:
   - Donchian Channel (20-period) breakout
   - ADX (14-period) > 25 for trend confirmation

2. **Risk Management**:
   - Stop Loss: ±1.5 × ATR from entry
   - Take Profit: ±3.0 × ATR from entry
   - Position Size: 4% of balance per trade (10x leverage)

3. **Phase Management**:
   - Phase 1: ¥15,000 → ¥25,000
   - Phase 2: ¥25,000 → ¥40,000
   - Phase 3: ¥40,000 → ¥50,000

## Project Structure

```
crypto_analysis/
├── data/                       # Collected cryptocurrency data
├── logs/                       # Trading logs
├── config.py                   # Configuration settings
├── crypto_data_collector.py    # Binance data collection
├── entry_exit_point_generator.py    # Strategy implementation
├── line_messaging_api.py       # LINE notification
├── run_analysis_pipeline.py    # Main orchestrator
└── requirements.txt            # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd crypto_analysis
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys in `config.py` or environment variables:
```bash
# .env file
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
LINE_CHANNEL_TOKEN=your_line_channel_token
LINE_USER_ID=your_line_user_id
ENABLE_LINE_NOTIFY=true
```

## Usage

### Running the Strategy

To run the strategy in simulation mode:
```bash
python run_analysis_pipeline.py --dry-run
```

To run with real notifications:
```bash
python run_analysis_pipeline.py
```

### Strategy Parameters

Key parameters can be adjusted in `config.py`:

```python
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
```

### LINE Notifications

The strategy sends notifications for:
- New trading signals
- Phase transitions
- Trade execution details

Example notification:
```
BTCUSDT 🚀 BUY @50000.00
SL 49800.00 / TP 50400.00
Size 0.1000 (Bal ¥15000)
```

## Automated Execution

The strategy can be run automatically using GitHub Actions:

1. Set up repository secrets:
   - `BINANCE_API_KEY`
   - `BINANCE_API_SECRET`
   - `LINE_CHANNEL_TOKEN`
   - `LINE_USER_ID`

2. The workflow runs every hour to check for new signals

## Risk Warning

This strategy involves significant risk. Always:
- Start with small position sizes
- Monitor performance closely
- Be prepared for drawdowns
- Never risk more than you can afford to lose

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# cryptodonchian
