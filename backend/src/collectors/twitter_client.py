"""
this file extract data from the Twitter API
"""

##imports:
import csv
import os
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import time



load_dotenv()



class TwitterClient:
    def __init__(self):
        bearer = os.getenv("TWITTER_BEARER_TOKEN")
        self.client = tweepy.Client(bearer_token=bearer, wait_on_rate_limit=True)

    def search_last_24h(self, query, max_results=10):
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=1)

        resp = self.client.search_recent_tweets(
            query=query,
            max_results=max_results,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            expansions="geo.place_id,author_id",
            tweet_fields=["created_at", "lang", "public_metrics", "geo"]
        )
        return resp


def save_to_csv(resp, filename="tweets.csv"):
    if not resp.data:
        print("No tweets found")
        return

    places_dict = {}
    if resp.includes and "places" in resp.includes:
        for place in resp.includes["places"]:
            places_dict[place.id] = place.full_name

    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['tweet_id', 'created_at', 'text', 'lang', 'retweet_count', 'reply_count', 'like_count',
                      'quote_count', 'location']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for tweet in resp.data:
            location_name = None
            if tweet.geo and 'place_id' in tweet.geo:
                place_id = tweet.geo['place_id']
                location_name = places_dict.get(place_id, None)

            writer.writerow({
                'tweet_id': tweet.id,
                'created_at': tweet.created_at,
                'text': tweet.text.replace('\n', ' '),
                'lang': tweet.lang,
                'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                'reply_count': tweet.public_metrics.get('reply_count', 0),
                'like_count': tweet.public_metrics.get('like_count', 0),
                'quote_count': tweet.public_metrics.get('quote_count', 0),
                'location': location_name or "Unknown"
            })
    print(f"Saved {len(resp.data)} tweets to {filename}")


def main():
    client = TwitterClient()
    queries = ["tel aviv", "jerusalem", "haifa"]

    for query in queries:
        print(f"Searching tweets for: {query}")
        resp = client.search_last_24h(query)
        save_to_csv(resp, filename=f"{query}_tweets.csv")
        print("Waiting 60 seconds before next request to avoid rate limit...")
        time.sleep(60)


if __name__ == "__main__":
    main()


