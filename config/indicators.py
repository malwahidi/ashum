# RSI
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD = 2.0

# Moving Averages
SMA_SHORT = 50
SMA_LONG = 200
EMA_FAST = 9
EMA_SLOW = 21

# Volume
VOLUME_AVG_PERIOD = 20
VOLUME_SPIKE_MULTIPLIER = 1.5

# Signal Scoring Weights
SCORE_RSI_MACD = 30       # RSI oversold/overbought + MACD crossover
SCORE_TREND = 15           # Price above/below SMA(200)
SCORE_BB_BOUNCE = 20       # Price at Bollinger Band
SCORE_VOLUME = 15          # Volume confirmation
SCORE_EMA_CROSS = 20       # EMA(9)/EMA(21) crossover
