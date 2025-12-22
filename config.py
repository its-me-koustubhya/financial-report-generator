from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
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

@lru_cache
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    This ensures settings are only loaded once and reused.
    """
    return Settings()

# Create global settings instance
settings = get_settings()

# Factory functions for LLMs (lazy loading)
def get_llm_factual(api_key: str = None):
    """Get LLM for factual data collection (low temperature)"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key= api_key or settings.GROQ_API_KEY,
        model=settings.MODEL_NAME,
        temperature=settings.collector_temperature
    )

def get_llm_balanced(api_key: str = None):
    """Get LLM for balanced analysis"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key= api_key or settings.GROQ_API_KEY,
        model=settings.MODEL_NAME,
        temperature=settings.analyst_temperature
    )

def get_llm_creative(api_key: str = None):
    """Get LLM for creative writing"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key= api_key or settings.GROQ_API_KEY,
        model=settings.MODEL_NAME,
        temperature=settings.writer_temperature
    )

def get_llm_precise(api_key: str = None):
    """Get LLM for precise editing"""
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key= api_key or settings.GROQ_API_KEY,
        model=settings.MODEL_NAME,
        temperature=settings.editor_temperature
    )

def get_tavily_client(api_key: str = None):
    """Get Tavily client (only when needed)"""
    from tavily import TavilyClient
    return TavilyClient(api_key= api_key or settings.TAVILY_API_KEY)

def search_web(query: str, api_key: str = None) -> list:
    """
    Search the web for information about a given query.
    
    Args:
        query: The search query string
        
    Returns:
        A list of search results with titles, URLs, and content
    """
    try:
        tavily_client = get_tavily_client(api_key)
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