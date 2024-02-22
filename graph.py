import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Load sentiment data
sentiment_df = pd.read_csv('AAPL_Sentiment_Separate.csv')
sentiment_df['published_date'] = pd.to_datetime(sentiment_df['published_date'])

# Rescale negative scores and calculate net sentiment
sentiment_df['excerpt_negative'] = sentiment_df['excerpt_negative'] * -1
sentiment_df['Net_Sentiment'] = sentiment_df['excerpt_positive'] + sentiment_df['excerpt_negative']

# Prepare daily sentiment scores
daily_sentiment = sentiment_df.groupby('published_date')['Net_Sentiment'].mean()

# Load price data for the same date range
equity = yf.Ticker("AAPL")
price_df = equity.history(
    start=sentiment_df['published_date'].min().strftime('%Y-%m-%d'),
    end=sentiment_df['published_date'].max().strftime('%Y-%m-%d'),
    interval='1d'
).reset_index()

# Calculate the daily percent change in closing prices
price_df['Percent_Change'] = price_df['Close'].pct_change()

# Ensure 'Date' is in datetime format
price_df['Date'] = pd.to_datetime(price_df['Date'])

# No need to scale sentiment for plotting against percent change
scaled_sentiment = daily_sentiment

# Plotting
fig, ax1 = plt.subplots(figsize=(14, 7))

color = 'tab:red'
ax1.set_xlabel('Date')
ax1.set_ylabel('Percent Change in Close', color=color)
ax1.plot(price_df['Date'], price_df['Percent_Change'], color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:blue'
ax2.set_ylabel('Sentiment', color=color)
ax2.plot(daily_sentiment.index, scaled_sentiment, color=color, alpha=0.5)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.title('AAPL Percent Change in Close and Sentiment Over Time')
plt.show()
