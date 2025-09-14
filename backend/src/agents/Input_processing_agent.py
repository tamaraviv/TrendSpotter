"""
Input processing agent

This agent is the entry point of the system.
It receives the raw question from the user and analyzes it to extract intent and requirements
(e.g., whether the user wants 1 trending song, the top 3, or another number).

Responsibilities:
- Interpret the user’s query and determine what information is being requested.
- Identify whether the user expects a single trend, multiple top trends, or another specific detail.
- Pass the processed question (with clarified intent) to the next agent in the pipeline.

"""

# ---------- imports ----------
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
import json


def clean_markdown_json(response: str) -> str:
    """
   This function is used to clean markdown json
    """
    lines = response.strip().splitlines()
    cleaned_lines = [line for line in lines if not (line.strip().startswith("```") or line.strip().startswith("```json"))]
    return "\n".join(cleaned_lines).strip()


class Input_processing_agent:
    def __init__(self,
                 instructions_file_path,
                 user_input,
                 gemini,
                 client_uri,
                 conversation_history_collection,
                 data_base):
        self.instructions_file_path = instructions_file_path
        self.user_input = user_input
        self.gemini = gemini
        self.client_uri = client_uri
        self.conversation_history_collection = conversation_history_collection
        self.data_base = data_base


    def process_input(self) -> dict:
        """
        This function is used to process the user input and store the conversation and analyse it
        :return:
        """
        with open(self.instructions_file_path, "r", encoding="utf-8") as f:
            instructions = f.read()

        client = self.client_uri
        db = client[self.data_base]
        collection = db[self.conversation_history_collection]

        conversation_history = []
        inserted_doc_id = None
        query_embedding = None


        conversation_history.append({"role": "user", "text": self.user_input})

        conversation_text = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['text']}" for msg in conversation_history]
        )
        prompt = f"{instructions}\n---\n{conversation_text}\nGemini:"

        response = self.gemini.chat.send_message(prompt)
        response_text = clean_markdown_json(response.text)

        try:
            parsed_response = json.loads(response_text)
        except json.JSONDecodeError:
            parsed_response = None

        if inserted_doc_id is None:
            query_embedding = self.gemini.get_embedding(self.user_input)

            doc = {
                "timestamp": datetime.utcnow(),
                "conversation": conversation_history,
                "gemini_response": parsed_response if isinstance(parsed_response, dict) else None,
                "embedding": query_embedding
            }
            inserted_doc = collection.insert_one(doc)
            inserted_doc_id = inserted_doc.inserted_id

        else:
            collection.update_one(
                {"_id": inserted_doc_id},
                {
                    "$set": {"gemini_response": parsed_response if isinstance(parsed_response, dict) else None},
                    "$push": {"conversation": {"$each": conversation_history[-2:]}}
                }
            )

        if isinstance(parsed_response, dict) and all(
            key in parsed_response for key in ["location", "type", "trend"]
        ):
            return {
                "_id": str(inserted_doc_id),
                "conversation": conversation_history,
                "gemini_response": parsed_response,
                "embedding": query_embedding
            }

        return {"message": "No complete trend-related query provided."}
