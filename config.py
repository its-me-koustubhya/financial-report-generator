import os
from langchain_groq import ChatGroq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY= os.getenv("TAVILY_API_KEY")
GROQ_API_KEY= os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv("MODEL_NAME")

# Temperature Settings
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
DEFAULT_TEMPERATURE = 0.7

# Search configuration
MAX_SEARCH_RESULTS = 5
SEARCH_DEPTH = "advanced"

# Report Configuration
OUTPUT_FORMAT = "markdown"
MAX_REPORT_LENGTH = 5000  # characters
MIN_SOURCES = 3

# for data collector
llm_factual = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.1
    )

# for analyst
llm_balanced = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.3
    )

# for writer
llm_creative = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.5
    )

# for editor
llm_precise = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.2
    )


# Validate API key exists
if not TAVILY_API_KEY:
    raise ValueError("TAVILY API KEY not found in environment variables")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def search_web(query: str) -> list:
    """
    Search the web for information about a given query.
    
    Args:
        query: The search query string
        
    Returns:
        A list of search results with titles, URLs, and content
    """
    try:
        response = tavily_client.search(query, max_results= MAX_SEARCH_RESULTS, search_depth= SEARCH_DEPTH,)

        if not response.get('results'):
            return []

        return response['results']
    
    except Exception as e:
        print(f'Error during search: {e}')
        return []
