import requests

api_key = "ddd65ace-0122-4337-b58b-b98b053ea228"
api_endpoint = "https://api.goperigon.com/v1/all"

# Define search parameters
search_params = {
    "apiKey": api_key, 
    "title": "tesla OR TSLA",
    "from": "2022-01-01",
    "to": "2023-01-01",
    "language": "en",
    "sortBy": "date",
    "topic": "Markets",
    "companySymbol": "TSLA",
    "showNumResults": "True",
    "size": 100,  # Number of articles to retrieve per page
}

# Make the API request
response = requests.get(api_endpoint, params=search_params)

if response.status_code == 200:
    # Parse the response JSON
    result = response.json()

    # Extract and print relevant information from the articles
    for article in result["articles"]:
        title = article.get("title", "")
        description = article.get("desc", "")
        content = article.get("content", "")
        publication_date = article.get("pubDate", "")

        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Publication Date: {publication_date}")
        print("\n---\n")

    # If you want to retrieve more pages, you can implement pagination logic using the 'relevance' parameter
    # Example: search_params["relevance"] = result.get("nextPage", 0)
else:
    print("Failed to fetch articles. Status code:", response.status_code)
    print(response.text)
