"""
LangChain Integration module.
Provides LangChain-based enhancements to the news pipeline.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the prediction market schema
class PredictionMarket(BaseModel):
    """Schema for a prediction market."""
    title: str = Field(description="The yes/no prediction question")
    description: str = Field(description="Detailed explanation of the prediction market")
    endTime: str = Field(description="ISO format end time for the prediction (e.g., 2025-12-31T23:59:59Z)")
    tags: List[str] = Field(description="List of 3 relevant tags for the prediction market")
    
    @validator('endTime')
    def validate_end_time(cls, v):
        """Validate that endTime is in ISO format."""
        try:
            # Check if it's in ISO format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            # Ensure it ends with Z
            if not v.endswith('Z'):
                raise ValueError("endTime must end with 'Z'")
            return v
        except Exception as e:
            raise ValueError(f"Invalid endTime format: {str(e)}")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate that there are exactly 3 tags."""
        if len(v) != 3:
            raise ValueError("Must provide exactly 3 tags")
        return v

def create_langchain_llm():
    """
    Create a LangChain LLM instance using Google Generative AI.
    
    Returns:
        LangChain LLM instance
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.2,
        top_p=0.95,
        top_k=40,
        max_output_tokens=1024,
    )
    
    return llm

def create_prediction_market_chain():
    """
    Create a LangChain chain for generating prediction markets.
    
    Returns:
        LangChain chain for generating prediction markets
    """
    # Create the LLM
    llm = create_langchain_llm()
    
    # Create the output parser
    parser = JsonOutputParser(pydantic_object=PredictionMarket)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_template("""
You are an expert at creating prediction market questions based on news articles.
I'll provide you with a news article, and I need you to create a Kalshi-style prediction market question.

Here's the article information:
Title: {title}
Category: {category}
Published Date: {published_date}
Source: {source}

Content:
{content}

Please create:
1. A clear yes/no prediction question based on the article (title)
2. A specific timeframe with a verifiable end date (endTime) in ISO format (YYYY-MM-DDThh:mm:ssZ)
3. A detailed explanation suitable for a financial prediction market (description)
4. Select exactly 3 relevant tags from this list: {available_tags}

{format_instructions}
""")
    
    # Create the chain
    chain = prompt | llm | parser
    
    return chain

def generate_prediction_market(article_data: Dict[str, Any], available_tags: List[str]) -> Optional[Dict[str, Any]]:
    """
    Generate a prediction market using LangChain.
    
    Args:
        article_data: Article data dictionary
        available_tags: List of available tags
        
    Returns:
        Prediction market data or None if generation failed
    """
    try:
        # Create the chain
        chain = create_prediction_market_chain()
        
        # Prepare the input
        content = article_data.get('processed_content', 
                   article_data.get('content', 
                   article_data.get('summary', '')))
        
        # Run the chain
        result = chain.invoke({
            "title": article_data["title"],
            "category": article_data["category"],
            "published_date": article_data["published_date"],
            "source": article_data["source"],
            "content": content,
            "available_tags": ", ".join(available_tags),
            "format_instructions": JsonOutputParser(pydantic_object=PredictionMarket).get_format_instructions()
        })
        
        # Add the original article data
        result["article"] = {
            "title": article_data["title"],
            "link": article_data["link"],
            "published_date": article_data["published_date"],
            "source": article_data["source"],
            "category": article_data["category"]
        }
        
        logger.info(f"Successfully generated prediction market: {result['title']}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating prediction market with LangChain: {str(e)}")
        return None
