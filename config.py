import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

# Temperature Settings
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
DEFAULT_TEMPERATURE = 0.7

# Search configuration
MAX_SEARCH_RESULTS = 5
SEARCH_DEPTH = "advanced"

# Report Configuration
OUTPUT_FORMAT = "markdown"
MAX_REPORT_LENGTH = 5000
MIN_SOURCES = 3

# Don't instantiate LLMs at import time - create factory functions instead
def get_llm_factual():
    """Get LLM for factual data collection (low temperature)"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.1
    )

def get_llm_balanced():
    """Get LLM for balanced analysis"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.3
    )

def get_llm_creative():
    """Get LLM for creative writing"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.5
    )

def get_llm_precise():
    """Get LLM for precise editing"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.2
    )

def get_tavily_client():
    """Get Tavily client (only when needed)"""
    from tavily import TavilyClient
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    return TavilyClient(api_key=TAVILY_API_KEY)

def search_web(query: str) -> list:
    """
    Search the web for information about a given query.
    
    Args:
        query: The search query string
        
    Returns:
        A list of search results with titles, URLs, and content
    """
    try:
        tavily_client = get_tavily_client()
        response = tavily_client.search(
            query, 
            max_results=MAX_SEARCH_RESULTS, 
            search_depth=SEARCH_DEPTH
        )

        if not response.get('results'):
            return []

        return response['results']
    
    except Exception as e:
        print(f'Error during search: {e}')
        return []