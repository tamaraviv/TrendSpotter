"""
Answer Agent

This agent is responsible for generating the final response that will be returned to the user.
It receives a ranked list of trends (already processed and sorted by popularity) and formulates
a clear and user-friendly answer according to the user's request.

Responsibilities:
- If the user asked for the single most trending item, return only the first entry from the ranked
 list.
- If the user asked for the top N items, return the first N entries in order.
- If the required information is missing or unclear, return "I don’t know".
- The response is generated with the help of an LLM (e.g., Gemini) and is formatted using a
predefined prompt.

In short, the Answer Agent transforms structured ranked data into a concise, human-readable answer
that directly matches the user’s question.
"""


# ---------- imports ----------
from bson import ObjectId


class Answer_agent:
    def __init__(self,
                 ranked_list,
                 conversation_history,
                 gemini,
                 conversation_history_collection,
                 client,
                 data_base,
                 last_user_input):
        self.ranked_list = ranked_list
        self.conversation_history = conversation_history
        self.gemini = gemini
        self.conversation_history_collection = conversation_history_collection
        self.client = client
        self.data_base = data_base
        self.last_user_input = last_user_input


    def process_answer(self):
        """
        This function generate an answer using LLM according to the ranked_tweets_list
        :return:
        """
        prompt = (
            "You are a helpful assistant in a chat session. "
            "The user and you have had the following conversation:\n"
            "{conversation}\n\n"
            "The last user message is:\n"
            "'{last_user_message}'\n\n"
            "Collected tweets:\n"
            "{ranked_tweets}\n\n"
            "Instructions for generating your response:\n"
            "- The 'Collected tweets' section contains all available tweets related to the topic.\n"
            "- Tweets are ranked: the trendiest/popular one is first, and the least popular is last.\n"
            "- Use ONLY the information found in the collected tweets database.\n"
            "- Always interpret the user's latest message in the context of the whole conversation.\n"
            "- Answer STRICTLY according to the user's request:\n"
            "   • If the user asks for the most popular trend, return ONLY the first tweet/entity.\n"
            "   • If the user asks for the top N trends, return EXACTLY the first N tweets/entities in ranked order.\n"
            "   • If the user asks for the 2nd, 3rd, or any specific rank, return ONLY that tweet/entity.\n"
            "- If the information is missing or unclear, respond with 'I don't know'.\n"
            "- Mention the trendiest entity by name and its location (if available in the tweets).\n"
            "- Provide context or description strictly based on what the tweets say (e.g., what happens there, why it is popular).\n"
            "- Write in a friendly and informative tone, as if giving a personal recommendation.\n"
            "- Keep the response concise, no more than 25 words.\n\n"
            "Output the response as a single, well-formed paragraph."
        ).format(
            conversation=self.conversation_history,
            last_user_message=self.last_user_input,
            ranked_tweets=self.ranked_list
        )

        llm_response = self.gemini.ask(prompt)
        return llm_response



    # def save_answer_db(self, llm_response):
    #     """
    #     This func save the gemini response in the conversation in the database.
    #     :param llm_response:
    #     :return:
    #     """
    #     db = self.client[self.data_base]
    #     collection = db[self.conversation_history_collection]
    #     collection.update_one(
    #         {"_id": ObjectId(self.conversation_id)},
    #         {"$push": {"conversation": {"role": "gemini", "text": llm_response}}}
    #     )


    def return_answer(self):
        """
        This func returns the gemini response and saves in the database.
        :return:
        """
        llm_response = self.process_answer()
        #self.save_answer_db(llm_response)
        return llm_response


