from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Keys - Required
    GROQ_API_KEY: str
    TAVILY_API_KEY: str
    
    # Database - Required in production
    DATABASE_URL: str
    
    # JWT Authentication
    SECRET_KEY: str 
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Model Configuration
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    
    # Temperature Settings
    min_temperature: float = 0.0
    max_temperature: float = 2.0
    default_temperature: float = 0.7
    
    # Search Configuration
    max_search_results: int = 5
    search_depth: str = "advanced"
    
    # Report Configuration
    output_format: str = "markdown"
    max_report_length: int = 5000
    min_sources: int = 3
    
    # Model configuration for different agents
    collector_temperature: float = 0.1
    analyst_temperature: float = 0.3
    writer_temperature: float = 0.5
    editor_temperature: float = 0.2
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Create global settings instance
settings = Settings()

# Factory functions for LLMs (lazy loading)
def get_llm_factual():
    """Get LLM for factual data collection (low temperature)"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model_name,
        temperature=settings.collector_temperature
    )

def get_llm_balanced():
    """Get LLM for balanced analysis"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model_name,
        temperature=settings.analyst_temperature
    )

def get_llm_creative():
    """Get LLM for creative writing"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model_name,
        temperature=settings.writer_temperature
    )

def get_llm_precise():
    """Get LLM for precise editing"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model_name,
        temperature=settings.editor_temperature
    )

def get_tavily_client():
    """Get Tavily client (only when needed)"""
    from tavily import TavilyClient
    return TavilyClient(api_key=settings.tavily_api_key)

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
            max_results=settings.max_search_results, 
            search_depth=settings.search_depth
        )

        if not response.get('results'):
            return []

        return response['results']
    
    except Exception as e:
        print(f'Error during search: {e}')
        return []