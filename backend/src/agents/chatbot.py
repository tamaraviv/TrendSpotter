"""
Chatbot loop runner on top of your existing Pipeline class.
Allows continuous conversation while preserving conversation history.
"""


# ---------- imports ----------
import pymongo
from add_to_git.TrendSpotter.backend.src.NLP import gemini_api
import Pipeline


# ---------- Setup ----------
client_ = pymongo.MongoClient("mongodb+srv://avivtamari:VZgOmJJyxnc5Rhzh@trendspotter.rcvrxee.mongodb.net/")
data_base_ = "trend_spotter"
tweets_collection_ = "trends_data_analyzed"
conversation_history_collection_ = "user_conversation_history"
gemini_ = gemini_api.Gemini().init_model("gemini-2.0-flash-lite")
instructions_file_path_ = "prompt_instructions.txt"
batch_size_ = 10
similarity_threshold = 0.6


def main():
    print("Chatbot started! Type 'exit' to quit.\n")
    user_input = input("user: ")
    pipeline = Pipeline.Pipeline(gemini_,
                                 data_base_,
                                 client_,
                                 conversation_history_collection_,
                                 tweets_collection_,
                                 instructions_file_path_,
                                 user_input,
                                 batch_size_,
                                 similarity_threshold)


    last_message = pipeline.run()

    print("gemini:", last_message)
    print("------------")


if __name__ == "__main__":
    main()
