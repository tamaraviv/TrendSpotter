"""
likes_agent.py

This module defines the `likes_agent` class, which is responsible for handling
operations related to "likes". The agent can be extended to include logic such as:
- Tracking the number of likes on a given item.
- Updating like counts when a user likes/unlikes.
- Providing analytics or reporting on popularity.

The design follows an object-oriented approach to allow flexibility and scalability.
Future improvements may include integration with a database or external API.
"""

# ---------- imports ----------
import json



class PopularityAgent:
    def __init__(self, analyzed_trends: list[dict], gemini):
        if isinstance(analyzed_trends, str):
            analyzed_trends = json.loads(analyzed_trends)
        self.analyzed_trends = analyzed_trends
        self.gemini = gemini

    def get_top_likes(self) -> dict:
        """
        Returns the trend with the highest number of likes, including:
        The list of tweets (text)
        The number of likes (likes)
        The number of tweets (count)
        """
        top_trend = max(self.analyzed_trends, key=lambda t: t["likes"])
        return {
            "tweets": top_trend["text"],
            "likes": int(top_trend["likes"]),
            "count": top_trend["count"]
        }


    def answer(self) -> str:
        """
        Returns a user-friendly summary of the trend including:
        - Popularity (trendiness)
        - Number of likes
        - Number of tweets
        """
        top_trend_data = self.get_top_likes()
        tweets = top_trend_data.get("tweets", [])
        likes = top_trend_data.get("likes", 0)
        count = top_trend_data.get("count", 0)

        prompt = f"""
        You are given a social media trend.

        Do NOT summarize the content of the trend.
        ONLY return a single sentence stating:
        - the trend in two - four words
        - The total number of likes: {likes}
        - The total number of tweets: {count}
        for example:
        - Intelligentsia Coffee place got 2282 likes and 5 people tweeted about it.
        - Yurakucho Kakida in Tokyo received 3490 likes and was mentioned in 4 tweets
        - Sushi No Midori garnered 1212 likes and appeared in 1 tweet.
        
        
        """

        answer = self.gemini.ask(prompt).strip()

        return answer
