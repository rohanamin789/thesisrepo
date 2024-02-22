import pandas as pd
from sklearn.metrics import mean_squared_error
from math import sqrt

def crosscorr(datax, datay, lag=0):
    """Lag-N cross correlation."""
    return datax.corr(datay.shift(lag))

# Load and prepare sentiment data
sentiment_df = pd.read_csv('JPMOrgan_Sentiment.csv')
sentiment_df['published_date'] = pd.to_datetime(sentiment_df['published_date'])
sentiment_df['title_negative'] = sentiment_df['title_negative'] * -1
sentiment_df['Net_Sentiment'] = sentiment_df['title_positive'] + sentiment_df['title_negative']
sentiment_daily_agg = sentiment_df.groupby('published_date')['Net_Sentiment'].sum()
sentiment_daily_agg.index = sentiment_daily_agg.index.tz_localize('UTC')

# Load and prepare price data from the CSV file
file_path = './Equities/JPM_daily.csv'
price_df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
price_df.index = price_df.index.tz_localize('UTC')
price_df['Price_Move'] = price_df['Close'].pct_change()

# No need to resample to month-end frequency for daily analysis
# sentiment_daily_agg and price_df['Price_Move'] are already in daily frequency

# Calculate cross-correlation for a range of daily lags
daily_lags = range(0, 30)  # Examines up to 30 days
cross_correlations = {lag: crosscorr(sentiment_daily_agg, price_df['Price_Move'], lag) for lag in daily_lags}

# Display cross-correlation results
for lag, corr in cross_correlations.items():
    print(f"Lag {lag} days: Cross-Correlation = {corr}")

# Identify and display the lag with the maximum cross-correlation
max_corr_lag = max(cross_correlations, key=cross_correlations.get)
max_corr_value = cross_correlations[max_corr_lag]
print(f"\nMaximum cross-correlation of {max_corr_value} occurs at a lag of {max_corr_lag} days.")

# Calculate RMSE for daily data
# Align sentiment and price data on their common dates and drop any rows with NA values in either Series
aligned_df = pd.concat([sentiment_daily_agg, price_df['Price_Move']], axis=1, join='inner').dropna()

# Extract the aligned and cleaned Series
sentiment_aligned_clean = aligned_df.iloc[:, 0]  # Assuming sentiment data is the first column
price_aligned_clean = aligned_df.iloc[:, 1]  # Assuming price movement data is the second column

# Calculate RMSE
rmse = sqrt(mean_squared_error(price_aligned_clean, sentiment_aligned_clean))

print(f"RMSE between daily aggregated net sentiment scores and daily price movements: {rmse}")
