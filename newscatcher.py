from newscatcherapi import NewsCatcherApiClient
# Default packages
import time
import csv
import os
import json


# Preinstalled packages
import requests
import pandas as pd
import json 



X_API_KEY = "Gvi1eow58jRpe-zRCzaehqwdbfgTXKutmxljxj_DN4E"

# URL of our News API
base_url = 'https://api.newscatcherapi.com/v2/search'
# Put your API key to headers in order to be authorized to perform a call
headers = {'x-api-key': X_API_KEY}




newscatcherapi = NewsCatcherApiClient(x_api_key=X_API_KEY)

# newscatcherapi = NewsCatcherApiClient(x_api_key=API_KEY)

news_articles = newscatcherapi.get_search_all_articles(q="Apple OR AAPL", lang = "en", published_date_precision = "date", search_in="title", from_ = "2023-01-01", to_ = "2023-12-31", topic = "business", by = "week")


data = news_articles.get('articles',[])

df = pd.json_normalize(data)
# df = pd.json_normalize(data, meta = ["status", "total_hits", "page", "total_pages", "page_size"])
# df = pd.DataFrame.from_dict(news_articles)
directory = "Equities"
if not os.path.exists(directory):
    os.makedirs(directory)
df.to_csv(f"{directory}/AppleFinance.csv", index=False)
