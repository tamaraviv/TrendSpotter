"""
Pipeline Runner

This file coordinates the full pipeline of agents to answer user questions.

Flow:
1. Orchestrator / Analyzer Agent
   - Receives the user’s question.
   - Interprets the intent (e.g., most popular, top 3 trends).
   - Passes a structured version of the request forward.

2. Data Agent
   - Queries the database (e.g., tweets).
   - Ranks the results using the scoring formula (likes + count).
   - Returns a sorted list of entities from trendiest to least.

3. Answer Agent
   - Takes the ranked list and the original user question.
   - Generates a clear, friendly response according to the rules:
       * If the user asks for the single trendiest → return the first.
       * If the user asks for the top N trends → return the first N.
       * If the info is missing → return "I don’t know".
   - Uses an LLM (e.g., Gemini) with a tailored prompt to produce the final response.

Purpose:
This file orchestrates the pipeline end-to-end, ensuring smooth communication between agents
and delivering the final answer to the user.
"""

# ---------- imports ----------
import Data_agent
import Input_processing_agent
import Answer_agent
import pymongo
from add_to_git.TrendSpotter.backend.src.NLP import gemini_api


client_ = pymongo.MongoClient("mongodb+srv://avivtamari:VZgOmJJyxnc5Rhzh@trendspotter.rcvrxee.mongodb.net/")
data_base_ = "trend_spotter"
tweets_collection_ = "trends_data_analyzed"
conversation_history_collection_ = "user_conversation_history"
gemini_ = gemini_api.Gemini().init_model("gemini-1.5-flash")
instructions_file_path_ = "prompt_instructions.txt"
batch_size_ = 10
similarity_threshold_ = 0.6



class Pipeline:
    """
    Coordinates: Orchestrator → DataAgent → AnswerAgent
    """

    def __init__(self,
                 gemini,
                 data_base,
                 client,
                 conversation_history_collection,
                 analyzed_tweets_collection,
                 instructions_file_path,
                 user_input,
                 batch_size,
                 similarity_threshold
                 ):

        self.gemini = gemini
        self.client = client
        self.data_base = data_base
        self.conversation_history_collection = conversation_history_collection
        self.analyzed_tweets_collection = analyzed_tweets_collection
        self.instructions_file_path = instructions_file_path
        self.user_input = user_input
        self.batch_size = batch_size
        self.similarity_threshold = similarity_threshold


    def run(self) -> str:
        """
        This func runs the pipeline and activate the three AI agents:
        1. understand intent
        2. get ranked list from data
        3. answer
        :return:
        """
        # 1. understand intent

        process_agent = Input_processing_agent.Input_processing_agent(
            self.instructions_file_path,
            self.user_input,
            self.gemini,
            self.client,
            self.conversation_history_collection,
            self.data_base)

        question_data = process_agent.process_input()

        conversation = question_data["conversation"]
        question_embedded = question_data["embedding"]
        conversation_id = question_data["_id"]


        # 2. get ranked list from data
        data_process_agent = Data_agent.DataAgent(self.client,
                                                  self.data_base,
                                                  self.gemini,
                                                  self.analyzed_tweets_collection,
                                                  conversation,
                                                  question_embedded,
                                                  self.batch_size,
                                                  self.similarity_threshold)

        ranked_list = data_process_agent.process_batch()

        # 3. answer
        process_answer_agent = Answer_agent.Answer_agent(ranked_list,
                                                         conversation,
                                                         self.gemini,
                                                         self.conversation_history_collection,
                                                         self.client,
                                                         self.data_base,
                                                         conversation_id)


        return process_answer_agent.return_answer()


def main():
    user_input_ = "what is the trendiest dance in paris?"
    pipe = Pipeline(gemini_,
                    data_base_,
                    client_,
                    conversation_history_collection_,
                    tweets_collection_,
                    instructions_file_path_,
                    user_input_,
                    batch_size_,
                    similarity_threshold_
                    )

    print(pipe.run())


if __name__ == "__main__":
    main()
