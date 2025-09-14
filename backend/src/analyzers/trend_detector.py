"""
This file extracts data from the database and analyzes it using Gemini LLM.
"""

# ---------- imports ----------
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import time



# ---------- Setup ----------
MAX_REQUESTS_PER_MINUTE = 15
SLEEP_BETWEEN_REQUESTS = 60 / MAX_REQUESTS_PER_MINUTE
year_ago_ = 360



def update_database(mongo_uri, file_path, data_base, collection_name):
    """
    This function updates the database with the data from the given CSV file
    :param mongo_uri:
    :param file_path:
    :param data_base:
    :param collection_name:
    :return:
    """
    client = mongo_uri
    db = client[data_base]
    collection = db[collection_name]

    df = pd.read_csv(file_path)
    data = df.to_dict(orient="records")
    collection.insert_many(data)


def get_tweets_last_year(client, data_base, collection_name, year_ago):
    """
    Extract tweets from the last year based on created_at_date field
    :param year_ago:
    :param client:
    :param data_base:
    :param collection_name:
    :return:
    """
    db = client[data_base]
    collection = db[collection_name]
    cursor = collection.find({"created_at_date": {"$gte": year_ago}})
    tweets = list(cursor)
    print(f"Found {len(tweets)} tweets from the last year.")
    return tweets


def build_batch_prompt(tweets_batch):
    """
    Build prompt with tweet text and location, asking LLM to extract general and
    specific types.
    :param tweets_batch:
    :return:
    """
    prompt = (
        "You are an expert in detecting trends from tweets.\n"
        "For each tweet, extract the following information as JSON:\n"
        "- general_type: broad category (food, drink, song, dance, etc.)\n"
        "- specific_type: detailed item (burger, pizza, latte, coffee, sushi, etc.)\n"
        "- location: where the trend is happening\n"
        "- trend: what the trend/topic is\n"
        "Only include facts explicitly mentioned or clearly implied.\n"
        "Respond only with JSON objects, one per tweet, in the same order as below.\n\n"
    )
    for i, tweet in enumerate(tweets_batch, 1):
        text = tweet.get('text', '')
        location = tweet.get('location', 'Unknown')
        prompt += f"{i}. Tweet: \"{text}\"\nLocation: {location}\n\n"
    prompt += "Output:\n"
    return prompt


def analyze_trends_batch(gemini, tweets_batch):
    """
    Use LLM to extract trend data including general and specific types.
    :param gemini:
    :param tweets_batch:
    :return:
    """
    prompt = build_batch_prompt(tweets_batch)
    try:
        response = gemini.generate(prompt)
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        # Ensure one line per tweet
        while len(lines) < len(tweets_batch):
            lines.append('{"general_type": null, "specific_type": null, "location": null, "trend": null}')
        return lines[:len(tweets_batch)]
    except Exception as e:
        return [f'Error: {e}'] * len(tweets_batch)


def generate_keywords(gemini: str, trend_analysis: str) -> list[str]:
    """
    Thia func activate LLM in order to extract keywords from tweets.
    :param gemini:
    :param trend_analysis:
    :return:
    """
    if not trend_analysis:
        return []

    text = str(trend_analysis)
    prompt = f"""
    Extract 5-10 short keywords (in English) that best capture the meaning of the following tweet.
    Return them as a comma-separated list.
    example - 
    1. tweet: **Food/Restaurant:** The user enjoyed the spicy tuna roll at Nobu, implying a 
        visit to the Nobu restaurant chain known for its sushi in Los Angeles. 
       after your analysis: spicy tuna roll , Nobu, restaurant chain, sushi, Los Angeles, food, restaurant 
    2. Tweet: Excited to attend the AI conference in San Francisco next week, hoping to learn about the latest machine learning trends.
       after your analysis: AI conference, San Francisco, machine learning, latest trends, learning
    3. Tweet: **Music:** The user is listening to a remix of the song "As It Was", implying the popularity of the song and its remixes in London.
       after your analysis: Music, As It Was, remix, Harry Styles, London, popular song
       
    Tweet: {text}
    """
    response = gemini.generate(prompt)
    raw_text = response.strip()
    keywords = [kw.strip() for kw in raw_text.split(",") if kw.strip()]
    return keywords


def aggregate_and_analyze_trends_with_gemini(gemini, client, data_base, collection_name,
                                             output_collection_name, BATCH_SIZE, year_ago):
    """
    Saves the analyzed trends data in a collection.
    :param year_ago:
    :param BATCH_SIZE:
    :param gemini:
    :param client:
    :param data_base:
    :param collection_name:
    :param output_collection_name:
    :return:
    """
    tweets_last_year = get_tweets_last_year(client, data_base, collection_name, year_ago)
    output_col = client[data_base][output_collection_name]

    new_docs = []
    requests_count = 0

    for i in range(0, len(tweets_last_year), BATCH_SIZE):
        batch = tweets_last_year[i: i + BATCH_SIZE]
        trends = analyze_trends_batch(gemini, batch)

        for tweet, trend_json in zip(batch, trends):
            tweet_text = tweet.get("text", "")

            tweet_embedding = gemini.get_embedding(tweet_text)
            requests_count += 1
            if requests_count % MAX_REQUESTS_PER_MINUTE == 0:
                print("⏳ Reached 15 requests, sleeping for 60 seconds...")
                time.sleep(60)
            else:
                time.sleep(SLEEP_BETWEEN_REQUESTS)

            try:
                trend_data = json.loads(trend_json)
            except json.JSONDecodeError:
                trend_data = {
                    "general_type": None,
                    "specific_type": None,
                    "location": None,
                    "trend": None
                }

            trend_analysis_text = trend_data.get("trend") or tweet_text

            # --- Generate keywords עם rate limit ---
            keywords = generate_keywords(gemini, trend_analysis_text)
            requests_count += 1
            if requests_count % MAX_REQUESTS_PER_MINUTE == 0:
                print("⏳ Reached 15 requests, sleeping for 60 seconds...")
                time.sleep(60)
            else:
                time.sleep(SLEEP_BETWEEN_REQUESTS)

            new_doc = {
                "_id": tweet.get("_id"),
                "tweet_id": tweet.get("tweet_id"),
                "created_at": tweet.get("created_at"),
                "location": trend_data.get("location") or tweet.get("location"),
                "type_general": trend_data.get("general_type"),
                "type_specific": trend_data.get("specific_type"),
                "created_at_date": tweet.get("created_at_date"),
                "trend_analysis": trend_analysis_text,
                "popularity": tweet.get("likes"),
                "embedding": tweet_embedding,
                "keywords": keywords
            }

            new_docs.append(new_doc)

    if new_docs:
        output_col.insert_many(new_docs)
        print(f"Inserted {len(new_docs)} documents into {output_collection_name}.")
    else:
        print("No tweets found")


def analyze_tweets_using_LLM(gemini, client, data_base, collection_name,
                             output_collection_name, BATCH_SIZE, year_ago):
    """
    This func analyze tweets using LLM
    :param year_ago:
    :param BATCH_SIZE:
    :param gemini:
    :param client:
    :param data_base:
    :param collection_name:
    :param output_collection_name:
    :return:
    """
    aggregate_and_analyze_trends_with_gemini(gemini, client, data_base, collection_name,
                                             output_collection_name, BATCH_SIZE, year_ago)
