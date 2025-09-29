"""
this file creates a fake CSV file with data
"""

# ---------- imports ----------
import csv
import sys
import os

from add_to_git.TrendSpotter.backend.src.NLP import gemini_api
from hakaton import gemini

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_tweets_with_gemini(gemini, start_num, tweets_count):
    prompt_instructions = f"""
    You are a data generator.
    Generate {tweets_count} fake tweets about trending topics, such as:
    - Trending places (cafes, bars, attractions, beaches, events)
    - Trending songs
    - Trending food and drinks
    - Trending dances
    - Trending festivals or shows
    - Mention the city/neighborhood/country.
    
    Rules:
    1. The dataset must be returned as a valid CSV encoded in UTF-8, with the following column headers: ["tweet_id", "text", "created_at", "location", "type", "hashtags", "likes"].
    2. "tweet_id" should start at {start_num} and increment by 1 for each subsequent row.
    3. "text" should be short, like a real tweet, with some repeating trending names so trends can be detected later.
    4. "created_at" should be a random date within the last 90 days, formatted as YYYY-MM-DD HH:MM:SS.
       The dates should be between May, June, July, and August of 2025.
    5. "location" should be real-world cities from different countries.
    6. "type" should be one of: ["place", "song", "food", "dance", "event", "beach", "festivals", "shows"].
    7. "hashtags" should contain 1–3 trending hashtags related to the tweet content, concatenated without spaces.
       For example: "#CumbiaChallenge#Dance" is correct; "#CumbiaChallenge #Dance" is incorrect.
    8. "likes" should be a random number between 1 and 2000.
    9. At least 40% of the tweets should be about several different repeated trends.
    This means there should be **at least 10 tweets for each of at least 4 different trending topics**, 
    so that multiple distinct trends appear repeatedly throughout the dataset.
    10. Return only the CSV content; do not include any explanations or extra text.

    """
    response = gemini.generate(prompt_instructions)

    return response


def create_tweets_csv(gemini, total_tweets, batch_size, start_num):
    with open("mock_data1.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = None

        for batch_start in range(0, total_tweets, batch_size):
            csv_chunk = generate_tweets_with_gemini(gemini, start_num, batch_size)

            rows = [r for r in csv_chunk.strip().split("\n") if r.strip()]

            if writer is None:
                writer = csv.writer(csvfile)
                header = rows[0].split(",")
                writer.writerow(header)
                data_rows = rows[1:]
            else:
                data_rows = rows[1:] if rows[0].startswith("tweet_id") else rows

            for row in data_rows:
                writer.writerow(row.split(","))

            start_num += batch_size

    print("✅ done!")


def tweets_into_csv(gemini, total_tweets, batch_size, start_id):
    """
    this func creates total_tweets mock tweets from gemini
    :param gemini:
    :param total_tweets:
    :param batch_size:
    :param start_id:
    :return:
    """
    create_tweets_csv(gemini, total_tweets, batch_size, start_id)


