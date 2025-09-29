"""
This file extracts data from the database and analyzes it using Gemini LLM.
guide:
set the date for the Mangodb can understand:
in the CMD run:
mongodb+srv://avivtamari:VZgOmJJyxnc5Rhzh@trendspotter.rcvrxee.mongodb.net/
then connect to the database and run - use trend_spotter
then run -
db.tweets_data_1.find().forEach(function(doc) {
let parts = doc.created_at.split(" "); // ["15/06/2025", "14:32"]
let dateParts = parts[0].split("/"); // ["15", "06", "2025"]
let timeParts = parts[1].split(":"); // ["14", "32"]

let dateObj = new Date(
    parseInt(dateParts[2]),     // year
    parseInt(dateParts[1]) - 1, // month (0-based)
    parseInt(dateParts[0]),     // day
    parseInt(timeParts[0]),     // hour
    parseInt(timeParts[1])      // minute
);

db.tweets_data_1.updateOne(
    { _id: doc._id },
    { $set: { created_at: dateObj, created_at_date: dateObj } }
);
});

"""

# ---------- imports ----------
import sys
import os
import pymongo
from add_to_git.TrendSpotter.backend.src.NLP import gemini_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from datetime import datetime, timedelta
import time


# ---------- Setup ----------
MAX_REQUESTS_PER_MINUTE = 15
SLEEP_BETWEEN_REQUESTS = 60 / MAX_REQUESTS_PER_MINUTE
year_ago_ = datetime.now() - timedelta(days=365)
BATCH_SIZE_ = 10


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
    Build prompt asking LLM to generate trend analysis only.
    Each tweet should produce one numbered analysis item.
    Includes both text and location fields.
    """
    prompt = (
        "You are an expert in detecting trends from tweets.\n"
        "For each tweet, provide a detailed trend analysis in one sentence.\n"
        "Each analysis should include:\n"
        "- A clear, human-readable title of the trend (like Travel/Tourism, Food/Restaurant, Music, etc.)\n"
        "- The location where the trend is happening (city, country if available)\n"
        "- If you infer that the trend is global, please mention ‘Global’\n"
        "- The specific style, activity, or item if mentioned\n"
        "- The name of any restaurant, bar, or place mentioned in the tweet\n"
        "- The trend itself and any user experience mentioned\n"
        "Format your response as a numbered list, one sentence per tweet, in the order of the tweets below.\n"
        "Respond only with the numbered trend analyses.\n\n"
        "Tweets:\n"
    )

    for i, tweet in enumerate(tweets_batch, 1):
        text = tweet.get('text', '').replace('"', '\\"')
        location = tweet.get('location').replace('"', '\\"')
        prompt += f"{i}. Tweet: \"{text}\" | Location: \"{location}\"\n"

    prompt += "\nTrend Analysis:\n"
    return prompt



def analyze_trends_batch(gemini_client, tweets_batch):
    """
    Send a batch of tweets to the LLM and parse the response into a list of trend analyses.
    Each element is a string representing one tweet's trend analysis.
    """
    prompt = build_batch_prompt(tweets_batch)

    response_text = gemini_client.generate(prompt)  # Assume this returns a string

    response_text = response_text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
    if response_text.endswith("```"):
        response_text = response_text.rsplit("```", 1)[0]

    analyses = []
    for line in response_text.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and line[1] == '.':
            analyses.append(line)

    return analyses


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


def aggregate_and_analyze_trends_with_gemini(
        gemini, client, data_base, collection_name,
        output_collection_name, BATCH_SIZE, year_ago):
    """
    Analyze only NEW tweets (not yet processed) and save them into the database.
    """
    tweets_last_year = get_tweets_last_year(client, data_base, collection_name, year_ago)
    output_col = client[data_base][output_collection_name]

    processed_ids = set(doc["tweet_id"] for doc in output_col.find({}, {"tweet_id": 1}))
    print(f"Found {len(processed_ids)} already processed tweets.")

    new_tweets = [tweet for tweet in tweets_last_year if tweet.get("tweet_id") not in processed_ids]
    print(f"{len(new_tweets)} new tweets to analyze.")

    requests_count = 0

    for i in range(0, len(new_tweets), BATCH_SIZE):
        batch = new_tweets[i: i + BATCH_SIZE]

        trends = analyze_trends_batch(gemini, batch)
        print(trends)

        for idx, tweet in enumerate(batch):
            if idx < len(trends):
                trend_analysis_text = trends[idx]
            else:
                trend_analysis_text = "No analysis generated"

            tweet_text = tweet.get("text", "")

            # --- Embedding ---
            tweet_embedding = gemini.get_embedding(tweet_text)
            requests_count += 1
            if requests_count % MAX_REQUESTS_PER_MINUTE == 0:
                print("⏳ Reached max requests, sleeping 60 seconds...")
                time.sleep(60)
            else:
                time.sleep(SLEEP_BETWEEN_REQUESTS)

            # --- Keywords ---
            keywords = generate_keywords(gemini, trend_analysis_text)
            requests_count += 1
            if requests_count % MAX_REQUESTS_PER_MINUTE == 0:
                print("⏳ Reached max requests, sleeping 60 seconds...")
                time.sleep(60)
            else:
                time.sleep(SLEEP_BETWEEN_REQUESTS)

            new_doc = {
                "_id": tweet.get("_id"),
                "tweet_id": tweet.get("tweet_id"),
                "created_at": tweet.get("created_at"),
                "created_at_date": tweet.get("created_at_date"),
                "trend_analysis": trend_analysis_text,
                "popularity": tweet.get("likes"),
                "embedding": tweet_embedding,
                "keywords": keywords
            }

            try:
                output_col.insert_one(new_doc)
                print(f"Inserted tweet {tweet.get('tweet_id')} into {output_collection_name}.")
            except Exception as e:
                print(f"Error inserting tweet {tweet.get('tweet_id')}: {e}")



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


if __name__ == "__main__":
    gemini_ = gemini_api.Gemini().init_model("gemini-2.0-flash")
    client_ = pymongo.MongoClient("mongodb+srv://avivtamari:VZgOmJJyxnc5Rhzh@trendspotter.rcvrxee.mongodb.net/")
    data_base_ = "trend_spotter"
    collection_name_not_analysed = "tweets_data"
    collection_name_output = "trends_data_analyzed_version2.0"
    file_path_ = "cleaned_tweets.csv"

    analyze_tweets_using_LLM(gemini_, client_, data_base_, collection_name_not_analysed, collection_name_output, BATCH_SIZE_, year_ago_)
