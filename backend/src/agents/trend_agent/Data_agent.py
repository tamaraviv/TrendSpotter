"""
Data Agent

This agent receives the processed question from the Input processing agent.
It is responsible for interacting with the database (e.g., collected tweets) to retrieve relevant
data.

Responsibilities:
- Query the database for entries related to the user’s request.
- Rank the retrieved results using a scoring formula (e.g., likes + count).
- Return a structured list of results, sorted from the trendiest to the least trendy.

"""

# ---------- imports ----------
import numpy as np
import json


def cosine_similarity(vec1, vec2):
    """
    Calculates the cosine similarity between two vectors.
    :param vec1:
    :param vec2:
    :return:
    """
    vec1, vec2 = np.array(vec1), np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def cosine_trendiest(no_duplicate_tweets):
    """
    Calculates the trendiest trend from a list of tweets.
    :param no_duplicate_tweets:
    :return:
    """
    if not no_duplicate_tweets:
        print("No tweets to get trendiest")
        return []

    if isinstance(no_duplicate_tweets, str):
        import json
        clean_str = no_duplicate_tweets.strip()
        if clean_str.startswith("```json"):
            clean_str = clean_str[len("```json"):].strip()
        if clean_str.startswith("```"):
            clean_str = clean_str[3:].strip()
        if clean_str.endswith("```"):
            clean_str = clean_str[:-3].strip()

        no_duplicate_tweets = json.loads(clean_str)

    for entry in no_duplicate_tweets:
        entry['trendiness'] = entry.get('likes', 0) + 200 * entry.get('count', 1)

    ranked_tweets_list = sorted(no_duplicate_tweets, key=lambda x: x['trendiness'], reverse=True)
    ranked_tweets_list = json.dumps(ranked_tweets_list, ensure_ascii=False, indent=2)
    return ranked_tweets_list


# ---------- Main Class ----------
class DataAgent:
    def __init__(self,
                 client,
                 db,
                 gemini,
                 analyzed_tweets_collection,
                 question_embedded,
                 batch_size,
                 similarity_threshold,
                 conversation_history):
        """
        alpha: weight for likes vs count
        sim_threshold: minimum cosine similarity to consider a tweet relevant
        """
        self.batch_size = batch_size
        self.client = client
        self.db = db
        self.gemini = gemini
        self.analyzed_tweets_collection = analyzed_tweets_collection
        self.question_embedded = question_embedded
        self.similarity_threshold = similarity_threshold
        self.conversation_history = conversation_history


    def filtered_tweets_by_embeddings(self):
        """
        An AI agent that filters tweets based on their embeddings and returns a relevant to the
        question list of tweets.
        :return:
        """
        db = self.client[self.db]
        tweets_coll = db[self.analyzed_tweets_collection]
        similarity_threshold = float(self.similarity_threshold)

        relevant_tweets = []
        question_vec = self.question_embedded

        for tweet in tweets_coll.find():
            tweet_text = tweet.get("trend_analysis")
            likes = tweet.get("popularity", 0)
            tweet_vec = tweet["embedding"]
            similarity = float(cosine_similarity(question_vec, tweet_vec))

            if similarity >= similarity_threshold:
                relevant_tweets.append({"text": tweet_text, "likes": likes})

        if not relevant_tweets:
            return None

        relevant_tweets = json.dumps(relevant_tweets, indent=2)

        filter_prompt = (
            "You are given the full conversation history between the user and a assistant. "
            "Your task is to answer based on the **last user message**, but always interpret it "
            "in the context of the entire conversation history.\n\n"
            
            "You will receive a list of tweets in JSON format. Each tweet has 'text' and 'likes'.\n"
            "Keep only tweets that are relevant to the user's question. Remove any tweet that is not relevant.\n"
            "for each tweet check: "
            "1. identify the location that the user is interested in, then for each tweet decide if the tweet"
            "is relevant to the user's location if not then ignore"
            "e.g., user location - united stats, New York is part of United States then a tweet"
            "of a trend in new york will get in and a tweet of a trend in tokyo will not get in.\n"
            "2. identify the users trend (e.g., song, restaurant, dance, car type), include only"
            "tweets that match that type"
            "(e.g., coffee shop can be considered a restaurant if it serves food)\n"
            "Return the filtered list in the same JSON format as received, without changing anything else.\n\n"
            f"User's question: \"{self.conversation_history}\"\n"
            f"Tweets: {relevant_tweets}"
        )

        filtered_tweets = self.gemini.ask(filter_prompt).strip()

        return filtered_tweets

    def deduplicate_tweets(self, filtered_tweets):
        """
         Takes a list of tweet dictionaries and returns a new list with unique 'text' entries.
         Likes from duplicate tweets are summed.
        :param filtered_tweets:
        :return:
        """
        if not filtered_tweets:
            print("No tweets to deduplicate")
            return []

        no_dup_prompt = f"""
        You are an assistant that receives a list of tweets in JSON format.
        Each tweet is a dictionary with 'text' and 'likes'.

        Your task is:
        1. Identify tweets that refer to the same thing(same song, same burger place, same bar),
         even if the text is different - according to the users question
        2. M Merge these duplicates into a single entry.
        3. Sum the 'likes' of all duplicates.
        4. Count the number of tweets that refer to the same thing and store it in 'count'.
        5. Return a JSON list of dictionaries with unique songs and their total likes.
        6. Keep the 'text' field as the most complete or representative description of the song.

        Example input:
        {filtered_tweets}

        Output:
        [
            {{
                  "text": [
            "... tweet text 1 ...",
            "... tweet text 2 ...",
            ...
        ],
                "likes": total_likes,
                "count": number_of_duplicates
            }},
            ...
        ]
        """
        no_duplicate_tweets = self.gemini.ask(no_dup_prompt).strip()
        return no_duplicate_tweets


    def process_batch(self):
        """
        Orchestrates the full pipeline for answering a user’s question:
        1. Extracts the question and generates its embedding via `analyze_question`.
        2. Filters tweets by semantic similarity to the question (`filtered_tweets_by_embeddings`).
        3. Removes duplicate tweets to avoid repetition (`deduplicate_tweets`).
        4. Ranks the remaining tweets/entities by trendiness using cosine similarity (`cosine_trendiest`).
        5. Generates a final answer for the user, formatted according to the original question
           (e.g., return the single most popular result or the top 3 results) via `generate_user_answer`.

        This function acts as the main entry point to run the pipeline end-to-end.
        :return: ranked_tweets_list
        """
        filtered_tweets = self.filtered_tweets_by_embeddings()
        no_duplicate_tweets = self.deduplicate_tweets(filtered_tweets)
        ranked_tweets_list = cosine_trendiest(no_duplicate_tweets)
        return ranked_tweets_list

