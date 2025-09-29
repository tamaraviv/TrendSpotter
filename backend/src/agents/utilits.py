

def get_ranked_list(input_agent):
    """
    מקבלת Input_processing_agent ומחזירה רשימה של dict:
    [{'trend': '...', 'likes': 123, 'tweets': 10}, ...]
    """
    # לדוגמה, אם Gemini החזיר את הנתונים בפורמט JSON
    gemini_data = input_agent.process_input().get("gemini_response", {})

    # כאן עושים מיפוי לטרנדים – דוגמה כללית
    ranked_list = []
    if gemini_data:
        for trend_item in gemini_data.get("trends", []):
            ranked_list.append({
                "trend": trend_item.get("trend_name", "unknown"),
                "likes": trend_item.get("likes", 0),
                "tweets": trend_item.get("tweets_count", 0)
            })

    return ranked_list
