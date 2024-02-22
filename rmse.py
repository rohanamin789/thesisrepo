import pandas as pd
from sklearn.metrics import mean_squared_error
from math import sqrt

# Load and prepare sentiment data
sentiment_df = pd.read_csv('JPMorgan_Sentiment.csv')
sentiment_df['published_date'] = pd.to_datetime(sentiment_df['published_date'])
sentiment_df['title_negative'] = sentiment_df['title_negative'] * -1  # Rescale negative scores to be between 0 and -1
sentiment_df['Net_Sentiment'] = sentiment_df['title_positive'] + sentiment_df['title_negative']  # Calculate net sentiment
sentiment_daily_agg = sentiment_df.groupby('published_date')['Net_Sentiment'].sum()
sentiment_daily_agg.index = sentiment_daily_agg.index.tz_localize('UTC')

# Load and prepare price data from the CSV file
file_path = './Equities/JPM_daily.csv'
price_df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
price_df.index = price_df.index.tz_localize('UTC')  # Make timezone-aware to match sentiment data
price_df['Price_Move'] = price_df['Close'].pct_change()

# Ensure both Series have the same dates for RMSE calculation
# Align sentiment and price data on their common dates
aligned_df = pd.concat([sentiment_daily_agg, price_df['Price_Move']], axis=1, join='inner').dropna()

# Extract the aligned and cleaned Series for RMSE calculation
sentiment_aligned_clean = aligned_df.iloc[:, 0]  # Assuming sentiment data is the first column
price_aligned_clean = aligned_df.iloc[:, 1]  # Assuming price movement data is the second column

# Calculate RMSE
rmse = sqrt(mean_squared_error(price_aligned_clean, sentiment_aligned_clean))

print(f"RMSE between daily aggregated net sentiment scores and daily price movements: {rmse}")
