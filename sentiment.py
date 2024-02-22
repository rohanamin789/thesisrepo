import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# Load the FinBERT model and tokenizer
model_name = "yiyanghkust/finbert-tone"  # FinBERT model fine-tuned for financial sentiment analysis
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Initialize the sentiment analysis pipeline with FinBERT
sentiment_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Load your CSV file
df = pd.read_csv('./Equities/Nvidia.csv')

def get_sentiment_scores(text):
    # Ensure text is a string
    if not isinstance(text, str):
        text = str(text)
    
    # Tokenize the text to check if it needs to be chunked
    tokens = tokenizer.tokenize(text)
    max_length = 512 - 2  # accounting for [CLS] and [SEP] tokens
    chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
    
    aggregated_scores = {'positive': 0, 'negative': 0, 'neutral': 0}
    for chunk in chunks:
        # Convert chunk back to string
        chunk_text = tokenizer.convert_tokens_to_string(chunk)
        # Process the chunk through the sentiment pipeline
        chunk_results = sentiment_pipeline(chunk_text)
        # Aggregate the scores
        for result in chunk_results:
            label = result['label'].lower()
            score = result['score']
            aggregated_scores[label] += score
    
    # Normalize the scores by the number of chunks to get the average
    num_chunks = len(chunks)
    for sentiment in aggregated_scores:
        aggregated_scores[sentiment] /= num_chunks
    
    return aggregated_scores

def process_row(row):
    title_scores = get_sentiment_scores(row['title'])
    excerpt_scores = get_sentiment_scores(row['excerpt'])
    
    # Prefix the scores with their source for differentiation
    title_scores = {f'title_{k}': v for k, v in title_scores.items()}
    excerpt_scores = {f'excerpt_{k}': v for k, v in excerpt_scores.items()}
    
    return {**title_scores, **excerpt_scores}

# Apply the function to each row of the DataFrame and expand the results into separate columns
expanded_scores = df.apply(process_row, axis=1, result_type='expand')

# Concatenate the new sentiment scores with the original DataFrame
df_final = pd.concat([df, expanded_scores], axis=1)

# Save the DataFrame with sentiment analysis results back to a new CSV file
df_final.to_csv('Nvidia_Sentiment.csv', index=False)
