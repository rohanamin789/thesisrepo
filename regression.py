import pandas as pd
import statsmodels.api as sm

# Load sentiment data
sentiment_df = pd.read_csv('AAPL_Sentiment_Separate.csv')
# Ensure 'published_date' is in datetime format
sentiment_df['published_date'] = pd.to_datetime(sentiment_df['published_date'])

# Rescale negative scores to be between 0 and -1
sentiment_df['excerpt_negative'] = sentiment_df['excerpt_negative'] * -1

# Sum positive and rescaled negative scores for a net sentiment score
sentiment_df['Net_Sentiment'] = sentiment_df['excerpt_positive'] + sentiment_df['excerpt_negative']

# Aggregate net sentiment scores daily
sentiment_daily = sentiment_df.groupby('published_date')['Net_Sentiment'].sum()

# Load price data
price_df = pd.read_csv('./Equities/AAPL_daily.csv')
# Ensure 'Date' is in datetime format
price_df['Date'] = pd.to_datetime(price_df['Date'])
# Calculate daily price moves as a percent change
price_df['Price_Move'] = price_df['Close'].pct_change()

# Align sentiment and price data by date
combined_df = pd.concat([sentiment_daily, price_df.set_index('Date')['Price_Move']], axis=1, join='inner').dropna()

# Regression analysis
X = sm.add_constant(combined_df['Net_Sentiment'])  # Adds a constant term to the predictor
y = combined_df['Price_Move']

model = sm.OLS(y, X).fit()
print(model.summary())
