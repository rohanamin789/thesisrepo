import pandas as pd
import yfinance as yf

# Load sentiment data
sentiment_df = pd.read_csv('AAPL_Sentiment_Separate.csv')
# Ensure 'published_date' is in datetime format
sentiment_df['published_date'] = pd.to_datetime(sentiment_df['published_date'])

# Rescale negative scores to be between 0 and -1
sentiment_df['title_negative'] = sentiment_df['title_negative'] * -1

# Sum positive and rescaled negative scores for a net sentiment score
sentiment_df['Net_Sentiment'] = sentiment_df['title_positive'] + sentiment_df['title_negative']

# Aggregate net sentiment scores by month
sentiment_monthly = sentiment_df.resample('M', on='published_date')['Net_Sentiment'].sum()

# Load price data
price_df = pd.read_csv('./Equities/AAPL_monthly.csv')
# Ensure 'Date' is in datetime format for consistency and ease of manipulation
price_df['Date'] = pd.to_datetime(price_df['Date'])
# Resample to get the first Open and last Close of each month for price moves
price_monthly = price_df.set_index('Date').resample('M').agg({'Open': 'first', 'Close': 'last'})
price_monthly['Price_Move'] = (price_monthly['Close'] - price_monthly['Open']) / price_monthly['Open']

# Prepare data for correlation analysis

# Calculate monthly percent change for price moves
price_monthly['Price_Move'] = price_monthly['Close'].pct_change()

# Ensure both DataFrames are aligned by month
combined_df = pd.concat([sentiment_monthly, price_monthly['Price_Move']], axis=1, join='inner').dropna()

# Calculate correlation
correlation = combined_df.corr()

print("Correlation matrix:")
print(correlation)
