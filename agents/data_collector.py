from typing import Dict
from graph.state import ReportState
from config import search_web, get_llm_factual

#response we get from tavily
# {
#   "query": "Who is Leo Messi?",
#   "answer": "Lionel Messi, born in 1987, is an Argentine footballer widely regarded as one of the greatest players of his generation. He spent the majority of his career playing for FC Barcelona, where he won numerous domestic league titles and UEFA Champions League titles. Messi is known for his exceptional dribbling skills, vision, and goal-scoring ability. He has won multiple FIFA Ballon d'Or awards, numerous La Liga titles with Barcelona, and holds the record for most goals scored in a calendar year. In 2014, he led Argentina to the World Cup final, and in 2015, he helped Barcelona capture another treble. Despite turning 36 in June, Messi remains highly influential in the sport.",
#   "images": [],
#   "results": [
#     {
#       "title": "Lionel Messi Facts | Britannica",
#       "url": "https://www.britannica.com/facts/Lionel-Messi",
#       "content": "Lionel Messi, an Argentine footballer, is widely regarded as one of the greatest football players of his generation. Born in 1987, Messi spent the majority of his career playing for Barcelona, where he won numerous domestic league titles and UEFA Champions League titles. Messi is known for his exceptional dribbling skills, vision, and goal",
#       "score": 0.81025416,
#       "raw_content": null,
#       "favicon": "https://britannica.com/favicon.png"
#     }
#   ],
#   "auto_parameters": {
#     "topic": "general",
#     "search_depth": "basic"
#   },
#   "response_time": "1.67",
#   "request_id": "123e4567-e89b-12d3-a456-426614174111"
# }

def data_collector_agent(state: ReportState) -> Dict:
    """
    Collects financial data about a company from web sources.
    
    Args:
        state: Current report state with user_input (company name)
        
    Returns:
        Dict with updated raw_data, data_sources, current_step, and messages
    """

    # company name/query about the company
    query = state['user_input'] 

    # Get keys from workflow config
    config = state.get("config", {})
    groq_key = config.get("groq_api_key")
    tavily_key = config.get("tavily_api_key")


    # prompt to generate queries
    query_prompt = f"""Generate 3 specific search queries to find financial information about {query}.
    Focus on: recent financial results, revenue, profit, market performance.
    Return only the queries, one per line, no numbering or extra text."""

    llm_factual = get_llm_factual(api_key=groq_key)
    query_response = llm_factual.invoke(query_prompt)

    messages_list = []

    # creating a list of queries from the query_response
    queries = []

    queries_text = query_response.content

    # Split by newlines to get individual queries
    queries = [q.strip() for q in queries_text.split('\n') if q.strip()]

    if not queries:
      return {
          "raw_data": [],
          "data_sources": [],
          "current_step": "data_collection",
          "messages": ["Error: Could not generate search queries."]
      }

    messages_list.append(f"Generated {len(queries)} search queries")
        
    # collecting all the data and sources from the response
    all_raw_data = []
    all_sources = []

    for q in queries:
      results = search_web(q, tavily_key)
      for result in results:
        if result.get('content'):  # Safety check
            all_raw_data.append(result['content'])
        if result.get('url'):
            all_sources.append(result['url'])

    company_name = query.split()[0]  # First word
    relevant_chunks = sum(1 for chunk in all_raw_data 
                         if company_name.lower() in chunk.lower())
    
    relevance_pct = (relevant_chunks / len(all_raw_data) * 100) if all_raw_data else 0
    
    if relevance_pct < 20:
        quality_note = f"⚠️ Low relevance: only {relevant_chunks}/{len(all_raw_data)} chunks mention company"
    else:
        quality_note = f"✅ Good relevance: {relevant_chunks}/{len(all_raw_data)} chunks mention company"
    
    messages_list.append(quality_note)

    if not all_raw_data:
      return {
          "raw_data": [],
          "data_sources": [],
          "current_step": "data_collection",
          "messages": ["Warning: No data found for the given query."]
      }
    
    messages_list.append(f"Collected {len(all_raw_data)} data chunks from {len(all_sources)} sources")

    return {
    "raw_data": all_raw_data,
    "data_sources": all_sources,
    "current_step": "data_collection",
    "messages": messages_list
    }

