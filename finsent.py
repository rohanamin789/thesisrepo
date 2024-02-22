import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import time
# Ensure you have the VADER lexicon downloaded
import nltk

class FinsentDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = self.create_connection(db_path)

    # Create a database connection
    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)
        return conn

    # Fetch headlines from the ticker's table within the date range
    def parser(self, ticker, start_date, end_date):
        try:
            # Convert start_date and end_date to Unix timestamps
            start_timestamp = int(time.mktime(start_date.timetuple()))
            end_timestamp = int(time.mktime(end_date.timetuple()))

            cursor = self.conn.cursor()
            query = f"""
            SELECT headline, datetime 
            FROM {ticker} 
            WHERE datetime >= {start_timestamp} AND datetime <= {end_timestamp}
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            # Convert Unix timestamp back to readable date format
            headlines = [(row[0], datetime.fromtimestamp(row[1])) for row in rows] 
            return headlines
        except sqlite3.Error as e:
            print(e)
            return []

    # Calculate sentiment for a specific period
    def get_sentiment_period(self, ticker, start_date, end_date):
        headlines = self.parser(ticker, start_date, end_date)
        sia = SentimentIntensityAnalyzer()
        df_output = pd.DataFrame()

        for headline, date in headlines:
            pol_score = sia.polarity_scores(headline)
            pol_score.update({"Ticker": ticker, "Headline": headline, "Date": date})
            df_output = pd.concat([df_output, pd.DataFrame([pol_score])], ignore_index=True)

        return df_output


   # Method to get sentiment for monthly periods
    def get_monthly_sentiments(self, ticker):
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 10, 20)
        months = [datetime(start_date.year, start_date.month + i, 1) for i in range((end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1)]

        monthly_sentiments = pd.DataFrame()
        for start in months:
            end = datetime(start.year + (start.month // 12), (start.month % 12) + 1, 1) - timedelta(days=1)
            if end > end_date:
                end = end_date
            monthly_data = self.get_sentiment_period(ticker, start.date(), end.date())
            monthly_data['Start_Date'] = start.date()
            monthly_data['End_Date'] = end.date()
            monthly_sentiments = pd.concat([monthly_sentiments, monthly_data], ignore_index=True)

        return monthly_sentiments

    # Calculate monthly price data from a CSV file
    def calculate_monthly_price_data(self, csv_file):
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        monthly_data = df.resample('M').agg({'Open': 'first', 'Close': 'last'})

        return monthly_data

    def aggregate_monthly_sentiments(weekly_sentiments):
        # Aggregate sentiment scores by month
        monthly_aggregated = weekly_sentiments.groupby(['Ticker', 'Start_Date', 'End_Date']).agg({
            'compound': 'mean',  # or 'sum' or 'median', depending on your requirement
            'pos': 'mean',
            'neu': 'mean',
            'neg': 'mean'
        }).reset_index()
        return monthly_aggregated

    def calculate_monthly_correlation(self, ticker, aggregated_monthly_sentiments, csv_file):
        monthly_price_data = self.calculate_monthly_price_data(csv_file)
        correlations = []

        for index, month in aggregated_monthly_sentiments.iterrows():
            start = month['Start_Date']
            end = month['End_Date']

            # Filter the monthly price data to match the sentiment data's date range
            filtered_monthly_price_data = monthly_price_data[(monthly_price_data.index >= pd.to_datetime(start)) & (monthly_price_data.index <= pd.to_datetime(end))].copy()

            # Check if there is corresponding price data for the sentiment data
            if not filtered_monthly_price_data.empty:
                # Calculate the price change
                filtered_monthly_price_data['Price_Change'] = filtered_monthly_price_data['Close'] - filtered_monthly_price_data['Open']

                # Calculate the correlation
                correlation_data = {
                    'compound': month['compound'],
                    'Price_Change': filtered_monthly_price_data['Price_Change'].iloc[0]
                }

                # Only proceed if there are non-null values
                if not np.isnan(correlation_data['compound']) and not np.isnan(correlation_data['Price_Change']):
                    correlation = np.corrcoef(correlation_data['compound'], correlation_data['Price_Change'])[0, 1]
                    correlations.append((start, end, correlation))

        return correlations





# Example usage:
db_path = './webscrap_headlines/output/2023-01-01_2023-10-24/financial_data.db'
csv_file = './AMZN Price Data.csv'  # Replace with your actual file path
ticker = 'AMZN_'  # Replace with your actual ticker

finsent_db = FinsentDB(db_path)
monthly_sentiments = finsent_db.get_monthly_sentiments(ticker)
print(monthly_sentiments)
monthly_correlations = finsent_db.calculate_monthly_correlation(ticker, monthly_sentiments, csv_file)

# Assuming you run this after calling calculate_weekly_correlation
for period in monthly_correlations:
    print(f"Week from {period[0]} to {period[1]}: Correlation = {period[2]}")
