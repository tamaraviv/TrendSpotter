"""
general_agent.py

The `GeneralAgent` class is responsible for providing general answers about a trend
the user is interested in. It uses the conversation history, Gemini LLM, and optionally
a WebSearchTool (DuckDuckGo) to generate responses. If the user asks something too
specific (like "How much is a ticket?"), the agent builds a clean web search query and
fetches info from the web.
"""

# ---------- imports ----------
from ddgs import DDGS



# ---------- Web Search Tool ----------
class DuckDuckGoAPI:
    def search(self, query: str):
        """
        Executes a DuckDuckGo web search and returns a list of results.
        """
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6))
        return results


class WebSearchTool:
    def __init__(self):
        pass

    def run(self, query: str) -> str:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6))

        if not results:
            return "I could not find this information online."

        snippets = [r.get("title") or r.get("body") or r.get("text") or r.get("snippet") or "" for r in results]
        snippets = [s for s in snippets if s]
        if not snippets:
            return "I could not find this information online."
        return "\n".join(snippets[:3])




# ---------- General Agent ----------
class GeneralAgent:
    def __init__(self, user_q, conversation_history, gemini, search_tool: WebSearchTool):
        self.user_q = user_q
        self.conversation_history = conversation_history
        self.gemini = gemini
        self.search_tool = search_tool

    def _extract_entity(self):
        """Use Gemini to extract the entity (place, festival, etc.) from previous conversation."""
        history_text = "\n".join(
            [f"{turn['role']}: {turn['content']}" for turn in self.conversation_history]
        )
        prompt = f"""
        Extract the main entity (place, festival, event, or brand) that the user is asking about
        in the next question based on the conversation history.

        Conversation history:
        {history_text}

        User's next question: {self.user_q}

        Provide ONLY the entity name. If none, respond 'None'.
        """
        entity = self.gemini.ask(prompt).strip()
        if entity.lower() in ['none', '']:
            return None
        return entity

    def _build_search_query(self, entity):
        """Combine entity with user's question for a precise search."""
        if entity:
            return f"{entity} {self.user_q}"
        else:
            return self.user_q

    def answer(self):
        entity = self._extract_entity()  # Monmouth Coffee Company
        query = f"{entity} address"
        web_context = self.search_tool.run(query)

        if "could not find" in web_context.lower():
            return web_context

        prompt = f"""
              You are a helpful assistant. Answer the user's question in ONE concise sentence.
              Use only the information from the conversation history or the following web context:
              {web_context}

              Conversation history:
              {"; ".join([f'{turn["role"]}: {turn["content"]}' for turn in self.conversation_history])}

              User question:
              {self.user_q}
              """

        answer = self.gemini.ask(prompt).strip()
        return answer