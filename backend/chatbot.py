"""
Chatbot Loop Runner

This script runs an interactive chatbot session on top of the existing TrendSpotter Pipeline.
It continuously reads user input, determines which agent should handle the request, and returns
the appropriate response while maintaining conversation history.

Features:
- Maintains a running history of the conversation.
- Uses the OrchestratorAgent to select the appropriate agent:
    * TrendAgent: Handles trend-related queries and returns ranked trends.
    * PopularityAgent: Handles popularity-specific questions about trends (likes, tweet counts).
    * GeneralAgent: Handles general questions using web search tools.
- Supports continuous conversation until the user types 'exit'.
- Interfaces with MongoDB for trend and conversation data.
- Uses the Gemini LLM model to generate natural, human-like responses.
- Configurable batch size and similarity threshold for ranking trends.

Setup:
- Connects to MongoDB using credentials stored in 'credentials.py'.
- Loads LLM model via Gemini API.
- Reads prompt instructions from a text file.
"""


# ---------- imports ----------
import pymongo
from add_to_git.TrendSpotter.backend.src.NLP import gemini_api
from add_to_git.TrendSpotter.backend.src.agents.trend_agent import trend_pipeline
from add_to_git.TrendSpotter.backend.src.agents.orchestrator_agent import orchestrator_agent
from add_to_git.TrendSpotter.backend.src.agents.general_agent import general_agent
from add_to_git.TrendSpotter.backend.src.agents.likes_agent import likes_agent
from add_to_git.TrendSpotter.backend.credentials import client_id, gemini_model

# ---------- Setup ----------
client_ = pymongo.MongoClient(client_id)
data_base_ = "trend_spotter"
tweets_collection_ = "trends_data_analyzed"
conversation_history_collection_ = "user_conversation_history"
gemini_ = gemini_api.Gemini().init_model(gemini_model)
instructions_file_path_ = "prompt_instructions.txt"
batch_size_ = 10
similarity_threshold = 0.6


def main():
    print("Chatbot started! Type 'exit' to quit.\n")

    conversation_history = []
    ranked_list = []

    while True:
        last_user_input = input("user: ")
        if last_user_input.lower() == "exit":
            print(conversation_history)
            print("Chatbot ended.")
            break

        conversation_history.append({"role": "user", "content": last_user_input})
        agent = orchestrator_agent.OrchestratorAgent(last_user_input, gemini_).select_agent()

        if agent == "TrendAgent":
            trendpipeline = trend_pipeline.TrendAgent(
                gemini_,
                data_base_,
                client_,
                conversation_history_collection_,
                tweets_collection_,
                instructions_file_path_,
                last_user_input,
                batch_size_,
                similarity_threshold,
                conversation_history
            )

            last_message, ranked_list = trendpipeline.pipline()
        elif agent == "PopularityAgent":
            if ranked_list:
                popularity_agent = likes_agent.PopularityAgent(ranked_list, gemini_)
                last_message = popularity_agent.answer()
            else:
                last_message = "Popularity data not available yet."

        elif agent == "GeneralAgent":
            search_tool = general_agent.WebSearchTool()
            generalagent = general_agent.GeneralAgent(last_user_input, conversation_history, gemini_, search_tool)
            last_message = generalagent.answer()

        else:
            last_message = "I can answer your question"

        conversation_history.append({"role": "assistant", "content": last_message})

        print("gemini:", last_message)
        print("------------")


if __name__ == "__main__":
    main()
