import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ashum:ashum@localhost:5432/ashum")

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Tadawul Market Hours (Asia/Riyadh UTC+3)
MARKET_TIMEZONE = "Asia/Riyadh"
MARKET_OPEN_HOUR = 10
MARKET_OPEN_MINUTE = 0
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 0
MARKET_DAYS = ["sun", "mon", "tue", "wed", "thu"]  # Sunday-Thursday

# Scheduler
SCAN_DELAY_MINUTES = 15  # Minutes after market open for first scan
INTRADAY_INTERVAL_MINUTES = 30  # Intraday scan interval

# Data
HISTORY_PERIOD = "1y"  # Default history period for analysis
MIN_HISTORY_DAYS = 200  # Minimum days needed for SMA(200)

# Signals
SIGNAL_THRESHOLD = 40  # Minimum score to trigger a signal
STRONG_THRESHOLD = 70  # Strong signal (high confidence)
MODERATE_THRESHOLD = 55  # Moderate signal (worth watching)
TOP_SIGNALS_COUNT = 10  # Max signals to send per scan

# Risk Management
STOP_LOSS_PERCENT = 3.0  # Default stop-loss: 3% below entry
TAKE_PROFIT_PERCENT = 6.0  # Default take-profit: 6% above entry (2:1 ratio)
TRAILING_STOP_ACTIVATION = 99.0  # Disabled for now
TRAILING_STOP_DISTANCE = 1.5  # Trail distance
MAX_HOLDING_DAYS = 10  # Max days to hold a trade
