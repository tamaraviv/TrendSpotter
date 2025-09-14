"""
this func runs the backend of the software
"""


# ---------- imports ----------
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pymongo import MongoClient
from add_to_git.TrendSpotter.backend.src.analyzers import trend_detector
from add_to_git.TrendSpotter.backend.src.processors import text_cleaner
from add_to_git.TrendSpotter.backend.src.NLP import gemini_api
from add_to_git.TrendSpotter.backend.src.collectors import prototype


# ---------- Setup ----------
gemini_ = gemini_api.Gemini().init_model("gemini-1.5-flash")
total_tweets_ = 100
batch_size_ = 100
start_id_ = 1
input_csv_path_ = "mock_data.csv"
output_csv_path_ = "clean_mock_data.csv"
client_ = MongoClient("mongodb+srv://avivtamari:VZgOmJJyxnc5Rhzh@trendspotter.rcvrxee.mongodb.net/")
data_base_ = "treck_spotter"
collection_name_ = "tweets_data"
output_collection_name_ = "trends_data"
output_collection_name_analyze_tweets_ = "trends_data_analyzed"
now = datetime.utcnow()
year_ago = datetime.utcnow() - timedelta(days=700)
BATCH_SIZE = 10


def tweets_into_database(gemini, total_tweets, batch_size, start_id, input_csv_path, output_csv_path):
    prototype.tweets_into_csv(gemini, total_tweets, batch_size, start_id)
    text_cleaner.generate_clean_tweets_csv(input_csv_path, output_csv_path)
    trend_detector.analyze_tweets_using_LLM(gemini, client_, data_base_, collection_name_,
                                            output_collection_name_analyze_tweets_)


