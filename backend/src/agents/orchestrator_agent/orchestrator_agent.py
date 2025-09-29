"""
OrchestratorAgent

This agent receives a user question and decides, using an LLM (Gemini),
which specialized agent should handle the question. It returns only the
name of the selected agent as a string.
"""

class OrchestratorAgent:
    def __init__(self, user_question, gemini):
        self.user_question = user_question
        self.gemini = gemini

    def select_agent(self):
        """
        Uses the LLM to determine which agent is best suited for the question.
        Returns the name of the agent as a string: 'TrendAgent', 'PopularityAgent',
        'GeneralAgent', or 'UnknownAgent'.
        """
        prompt = f"""
                You are an intelligent orchestrator. Your task is to choose the best agent
                to answer the user's question. The available agents are:
            
                1. TrendAgent - answers questions about current trends in general, most popular places
                best places.
                2. PopularityAgent - answers questions about the number of likes or the number
                 of tweets about this trend.
                3. GeneralAgent - use only for specific follow-up questions that require concrete details 
                  about a trend (addresses, prices, performers, dates, locations, etc.).
                4. Unknown - use this if none of the above agents are appropriate.
            
                User question:
                {self.user_question}
            
                Instruction:
                Based on the question, return **only** the name of the most appropriate agent
                from the list above, as a single word (no explanation).
                """
        agent_name = self.gemini.ask(prompt).strip()
        return agent_name



"""
from add_to_git.TrendSpotter.backend.src.NLP import gemini_api

gemini_model = "gemini-2.0-flash"
gemini_ = gemini_api.Gemini().init_model(gemini_model)
user_q = "what is the rank of this song on spotipy"
new_agent = OrchestratorAgent(user_q, gemini_)
print(new_agent.select_agent())
"""