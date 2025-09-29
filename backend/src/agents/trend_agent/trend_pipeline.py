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
from . import Data_agent
from . import Input_processing_agent
from . import Answer_agent
# import pymongo
# from add_to_git.TrendSpotter.backend.src.NLP import gemini_api
#
#
# client_ = pymongo.MongoClient("mongodb+srv://avivtamari:VZgOmJJyxnc5Rhzh@trendspotter.rcvrxee.mongodb.net/")
# data_base_ = "trend_spotter"
# tweets_collection_ = "trends_data_analyzed"
# conversation_history_collection_ = "user_conversation_history"
# gemini_ = gemini_api.Gemini().init_model("gemini-1.5-flash")
# instructions_file_path_ = "prompt_instructions.txt"
# batch_size_ = 10
# similarity_threshold_ = 0.6



class TrendAgent:
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
                 last_user_input,
                 batch_size,
                 similarity_threshold,
                 conversation_history,
                 ):

        self.gemini = gemini
        self.client = client
        self.data_base = data_base
        self.conversation_history_collection = conversation_history_collection
        self.analyzed_tweets_collection = analyzed_tweets_collection
        self.instructions_file_path = instructions_file_path
        self.batch_size = batch_size
        self.similarity_threshold = similarity_threshold
        self.conversation_history = conversation_history
        self.last_user_input = last_user_input

    def get_ranked_list(self, question_embedded) -> list:
        data_process_agent = Data_agent.DataAgent(self.client,
                                                  self.data_base,
                                                  self.gemini,
                                                  self.analyzed_tweets_collection,
                                                  question_embedded,
                                                  self.batch_size,
                                                  self.similarity_threshold,
                                                  self.conversation_history)

        return data_process_agent.process_batch()


    def pipline(self) -> str:
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
            self.last_user_input,
            self.gemini,
            self.client,
            self.conversation_history_collection,
            self.data_base,
            self.last_user_input,
            self.conversation_history)

        clarification = process_agent.check_and_clarify()
        while clarification is not None:
            return clarification, []

        question_embedded = process_agent.return_embedding()

        # 2. get ranked list from data
        ranked_list = self.get_ranked_list(question_embedded)

        # 3. answer
        process_answer_agent = Answer_agent.Answer_agent(ranked_list,
                                                         self.conversation_history,
                                                         self.gemini,
                                                         self.conversation_history_collection,
                                                         self.client,
                                                         self.data_base,
                                                         self.last_user_input)

        answer_text = process_answer_agent.return_answer()
        return answer_text, ranked_list
