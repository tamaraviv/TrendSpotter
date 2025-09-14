# TrendSpotter
A social media analytics tool that analyzes Twitter data to detect emerging trends and popular topics. Uses NLP and embeddings to identify key patterns, rank topics by frequency, engagement, and location, providing actionable insights in real time.
=======
TrendSpotter/
├── backend/
│   ├── src/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── config.py               # env loading, constants
│   │   ├── collectors/
│   │   │   └── twitter_client.py   # חיבור ל-Twitter וקריאות API
│   │   ├── processors/
│   │   │   ├── text_cleaner.py     # ניקוי טקסט, tokenization
│   │   │   └── location_extractor.py
│   │   ├── analyzers/
│   │   │   └── trend_detector.py   # אלגוריתם זיהוי טרנדים
│   │   ├── agents/
│   │   │   └── trend_agent.py      # סוכן שמריץ איסוף/ניתוח
│   │   ├── db/
│   │   │   ├── models.py           # SQLAlchemy models / migrations
│   │   │   └── repository.py       # פונקציות שמירת ושליפת נתונים
│   │   ├── api/
│   │   │   └── endpoints.py        # routes: /trends, /ask, /status
│   │   └── utils/
│   │       ├── logger.py
│   │       └── geocode.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── TrendsList.jsx
│   │   │   └── MapView.jsx
│   │   └── api.js                  # קריאות ל-backend
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md






import pymongo
import json
import google.generativeai as genai
from datetime import datetime
import NLP.gemini_api as gemini_api

# Configure your Gemini API key (replace with your actual key)
genai.configure(api_key="C:\\Users\\avivt\\PycharmProjects\pythonLab1\\add_to_git\TrendSpotter\\trendtracker-e8367-7af76b6d0788.json")

# Connect to MongoDB (adjust the connection string as needed, e.g., for cloud-hosted MongoDB)
client = pymongo.MongoClient("mongodb+srv://avivtamari:VZgOmJJyxnc5Rhzh@trendspotter.rcvrxee.mongodb.net/")
db = client["trend_spotter"]  # Replace with your actual DB name
tweets_collection = db["trends_data_analyzed"]  # Collection for stored tweets
queries_collection = db["user_input_data"]  # Collection for storing user questions and analyses (based on your example)
gemini_ = gemini_api.Gemini().init_model("gemini-2.0-flash")

class TrendAgent:
    def __init__(self):
        self.model = gemini_  # Use a suitable Gemini model; adjust if needed

    def analyze_question(self, question):
        """
        Uses Gemini to analyze the user question and extract location, type, and trend.
        Returns a dict with the extracted info.
        """
        prompt = f"""
        Analyze the following user question and extract the following in JSON format:
        - location: The main location mentioned (e.g., city or area).
        - type: The type of place or category (e.g., 'beach', 'pizza', 'restaurant').
        - trend: A short phrase describing the trend or what the user is seeking (e.g., 'best pizza').

        Question: {question}

        Output only valid JSON.
        """
        response = self.model.ask(prompt)
        try:
            # Parse the response as JSON (assuming Gemini returns text that can be parsed as JSON)
            analysis = json.loads(response.text)
            return analysis
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return {"location": "", "type": "", "trend": ""}


    def store_query_analysis(self, question, analysis):
        """
        Stores the user question and Gemini analysis in the queries collection.
        """
        doc = {
            "user_question": question,
            "gemini_response": analysis,
            "timestamp": datetime.utcnow()
        }
        result = queries_collection.insert_one(doc)
        return result.inserted_id


    def compute_popularity(self, location, place_type):
        """
        Queries the tweets collection to compute a weighted popularity score for each specific place.
        - Groups by specific location (assuming 'location' field in tweets is the specific place name).
        - Count: Number of mentions (tweets referencing the place).
        - Total likes: Sum of popularity (likes) across those tweets.
        - Score: Weighted as count * 1 + total_likes * 0.01 (adjust weights as needed).
        Returns the most popular place based on the highest score.
        """
        # Build query to match tweets relevant to the broader location and type
        query = {
            "location": {"$regex": location, "$options": "i"},  # Case-insensitive partial match for location
            "type": place_type
        }

        # Aggregation pipeline to group, compute scores, and sort
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$location",  # Group by specific location (place)
                "mention_count": {"$sum": 1},
                "total_likes": {"$sum": "$popularity"}
            }},
            {"$project": {
                "place": "$_id",
                "score": {
                    "$add": [
                        "$mention_count",  # Weight for mentions (e.g., 1 per mention)
                        {"$multiply": ["$total_likes", 0.01]}
                        # Weight for likes (adjust 0.01 to balance; e.g., 0.01 means 100 likes = 1 mention)
                    ]
                }
            }},
            {"$sort": {"score": -1}},  # Sort descending by score
            {"$limit": 1}  # Get the top one
        ]

        results = list(tweets_collection.aggregate(pipeline))
        if results:
            return results[0]["place"]
        return None

    def run(self, question):
        """
        Main method to process a user question:
        1. Analyze with Gemini.
        2. Store analysis in DB.
        3. Compute the most popular place based on tweets.
        4. Return the result.
        """
        print(f"Processing question: {question}")

        # Step 1: Analyze question
        analysis = self.analyze_question(question)
        if not analysis.get("location") or not analysis.get("type"):
            return "Unable to analyze the question properly."

        # Step 2: Store in DB
        query_id = self.store_query_analysis(question, analysis)
        print(f"Stored query analysis with ID: {query_id}")

        # Step 3: Compute trend/popularity
        popular_place = self.compute_popularity(analysis["location"], analysis["type"])
        if popular_place:
            return f"The most trendy {analysis['type']} in {analysis['location']} is: {popular_place}"
        else:
            return f"No relevant data found for {analysis['type']} in {analysis['location']}."


# Example usage
if __name__ == "__main__":
    agent = TrendAgent()
    user_question = "what is the most popular dance in barcelona?"
    result = agent.run(user_question)
    print(result)



