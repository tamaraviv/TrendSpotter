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
import sys
import os
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pymongo
from src.NLP import gemini_api
from src.agents.trend_agent import trend_pipeline
from src.agents.orchestrator_agent import orchestrator_agent
from src.agents.general_agent import general_agent
from src.agents.likes_agent import likes_agent
#from credentials import client_id, gemini_model

from pydantic import BaseModel # Added this import


# ---------- Setup ----------
data_base_ = "trend_spotter"
tweets_collection_ = "trends_data_analyzed"
conversation_history_collection_ = "user_conversation_history"
instructions_file_path_ = "prompt_instructions.txt"
batch_size_ = 10
similarity_threshold = 0.6

# ------------------- MongoDB -------------------
client_id = os.getenv("CLIENT_ID")

if not client_id:
    raise Exception("CLIENT_ID not set in environment variables")

client_ = pymongo.MongoClient(client_id)

# ------------------- Gemini -------------------
gemini_model = os.getenv("gemini_model")

if not gemini_model:
    raise Exception("GEMINI_MODEL not set in environment variables")

gemini_ = gemini_api.Gemini().init_model(gemini_model)



#----------- FastAPI -----------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os

app = FastAPI()

# הרשאות CORS לפרונט
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request body
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]


# Function to encapsulate chatbot logic
async def get_chatbot_response(user_message: str, conversation_history: list[dict]) -> str:
    global ranked_list # Use global to maintain state across calls

    # Append user message to history before processing
    conversation_history.append({"role": "user", "content": user_message})
    
    # Select agent based on the new user input
    agent = orchestrator_agent.OrchestratorAgent(user_message, gemini_).select_agent()

    last_message = ""

    if agent == "TrendAgent":
        trendpipeline = trend_pipeline.TrendAgent(
            gemini_,
            data_base_,
            client_,
            conversation_history_collection_,
            tweets_collection_,
            instructions_file_path_,
            user_message,  # Pass only the current user message
            batch_size_,
            similarity_threshold,
            conversation_history
        )

        last_message, ranked_list = await trendpipeline.pipline() # Await the pipeline
    elif agent == "PopularityAgent":
        if ranked_list:
            popularity_agent = likes_agent.PopularityAgent(ranked_list, gemini_)
            last_message = await popularity_agent.answer() # Await the answer
        else:
            last_message = "Popularity data not available yet. Please ask about trends first."

    elif agent == "GeneralAgent":
        search_tool = general_agent.WebSearchTool()
        generalagent = general_agent.GeneralAgent(user_message, conversation_history, gemini_, search_tool)
        last_message = await generalagent.answer() # Await the answer

    else:
        last_message = "I can't answer your question at the moment. Please try rephrasing."

    return last_message


# API endpoint for chat messages
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.messages:
        return JSONResponse({"error": "No messages provided"}, status_code=400)
    
    # Extract current user message and full conversation history
    user_message = request.messages[-1].content
    conversation_history_dicts = [msg.model_dump() for msg in request.messages[:-1]] # Convert Pydantic models to dicts for agent

    # Get chatbot response
    bot_response_content = await get_chatbot_response(user_message, conversation_history_dicts)

    # Add bot's response to the conversation history
    # Note: The conversation_history in get_chatbot_response already has the user message and will be updated with bot's response.
    # We return the new bot response content to the frontend.

    return JSONResponse({"role": "assistant", "content": bot_response_content})


# דוגמה ל־API
@app.get("/api/trends")
async def get_trends():
    return {"success": True, "trends": ["AI", "Crypto", "VR"]}

# Remove logo serving from backend, as it's a frontend asset
# LOCAL_LOGO_PATH = r"C:\Users\avivt\PycharmProjects\pythonLab1\add_to_git\TrendSpotter\frontend\website_logo.png"

# @app.get("/static/logo")
# async def logo():
#     if os.path.exists(LOCAL_LOGO_PATH):
#         return FileResponse(LOCAL_LOGO_PATH, media_type="image/png")
#     return JSONResponse({"error": "logo not found"}, status_code=404)


# Remove the old main function as it's no longer needed for FastAPI
# def main():
#     print("Chatbot started! Type 'exit' to quit.\n")

#     conversation_history = []
#     ranked_list = []

#     while True:
#         last_user_input = input("user: ")
#         if last_user_input.lower() == "exit":
#             print(conversation_history)
#             print("Chatbot ended.")
#             break

#         conversation_history.append({"role": "user", "content": last_user_input})
#         agent = orchestrator_agent.OrchestratorAgent(last_user_input, gemini_).select_agent()

#         if agent == "TrendAgent":
#             trendpipeline = trend_pipeline.TrendAgent(
#                 gemini_,
#                 data_base_,
#                 client_,
#                 conversation_history_collection_,
#                 tweets_collection_,
#                 instructions_file_path_,
#                 last_user_input,
#                 batch_size_,
#                 similarity_threshold,
#                 conversation_history
#             )

#             last_message, ranked_list = trendpipeline.pipline()
#         elif agent == "PopularityAgent":
#             if ranked_list:
#                 popularity_agent = likes_agent.PopularityAgent(ranked_list, gemini_)
#                 last_message = popularity_agent.answer()
#             else:
#                 last_message = "Popularity data not available yet."

#         elif agent == "GeneralAgent":
#             search_tool = general_agent.WebSearchTool()
#             generalagent = general_agent.GeneralAgent(last_user_input, conversation_history, gemini_, search_tool)
#             last_message = generalagent.answer()

#         else:
#             last_message = "I can't answer your question"

#         conversation_history.append({"role": "assistant", "content": last_message})

#         print("gemini:", last_message)
#         print("------------")


if __name__ == "__main__":
    # Use uvicorn to run the FastAPI app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
