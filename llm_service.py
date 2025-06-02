"""
LLM Service module.
Handles interaction with Gemini 1.5 Flash or equivalent LLM.
"""
import os
import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
import google.generativeai as genai
from config import LLM_CONFIG, AVAILABLE_TAGS, CATEGORY_STRUCTURE, PIPELINE_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the LLM
def initialize_llm():
    """
    Initialize the LLM client.

    Returns:
        Initialized LLM client
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    logger.info(f"Initialized LLM with model: {LLM_CONFIG['model']}")

    return genai.GenerativeModel(
        model_name=LLM_CONFIG["model"],
        generation_config={
            "temperature": LLM_CONFIG["temperature"],
            "max_output_tokens": LLM_CONFIG["max_output_tokens"],
            "top_p": LLM_CONFIG["top_p"],
            "top_k": LLM_CONFIG["top_k"],
        }
    )

def generate_prediction_content(model, article_data: Dict[str, Any], max_retries: int = PIPELINE_CONFIG["max_retries"]) -> Optional[Dict[str, Any]]:
    """
    Generate prediction market content using the LLM.

    Args:
        model: LLM model instance
        article_data: Article data dictionary
        max_retries: Maximum number of retries for LLM calls

    Returns:
        Dictionary with prediction market content or None if generation failed
    """
    # Get relevant subcategories for the article's category
    category = article_data.get('category', 'Trending')
    relevant_subcategories = []
    if category in CATEGORY_STRUCTURE:
        relevant_subcategories = CATEGORY_STRUCTURE[category]['subcategories']

    prompt = f"""
You are an expert at creating prediction market questions based on news articles.
I'll provide you with a news article, and I need you to create a Kalshi-style prediction market question.

Here's the article information:
Title: {article_data['title']}
Category: {article_data['category']}
Published Date: {article_data['published_date']}
Source: {article_data['source']}

Content:
{article_data.get('processed_content', article_data.get('content', article_data.get('summary', '')))}

CATEGORY CONTEXT:
This article is categorized under "{category}". When selecting tags, prioritize subcategories from this category:
{', '.join(relevant_subcategories) if relevant_subcategories else 'General subcategories'}

Please create:
1. A clear yes/no prediction question based on the article (title)
2. A specific timeframe with a verifiable end date (endTime)
3. A detailed explanation suitable for a financial prediction market (description)
4. Select exactly 3 relevant tags from this list: {', '.join(AVAILABLE_TAGS)}
   - Prioritize tags that match the article's category and subcategories
   - Choose the most specific and relevant tags for the content

Format your response as a JSON object with these fields:
- title: The yes/no prediction question
- endTime: The ISO 8601 date when the prediction will be resolved (YYYY-MM-DDThh:mm:ssZ)
- description: A detailed explanation (2-3 paragraphs)
- tags: Array of exactly 3 tags from the provided list

IMPORTANT GUIDELINES:
- The question must be objectively verifiable at the end date with clear resolution criteria
- The question should be specific and avoid ambiguity
- The timeframe should be reasonable (typically 1-12 months in the future)
- For events with uncertain dates, set the endTime to a date when we'll definitely know the outcome
- The explanation should provide context, reasoning, and clear resolution criteria
- The explanation should be 2-3 paragraphs long and include:
  * Background information from the article
  * What constitutes a "YES" outcome
  * What constitutes a "NO" outcome
  * Any relevant factors investors should consider
- Choose the 3 most relevant tags that match the content from the provided list only
- Make sure the question is interesting and has genuine uncertainty (avoid obvious outcomes)

JSON RESPONSE FORMAT ONLY:
"""

    retry_count = 0
    while retry_count < max_retries:
        try:
            response = model.generate_content(prompt)

            # Extract the JSON from the response
            response_text = response.text

            # Find JSON content (it might be wrapped in markdown code blocks)
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = response_text.strip()

            # Parse the JSON
            prediction_data = json.loads(json_text)

            # Validate the response
            if validate_prediction_data(prediction_data):
                return prediction_data
            else:
                logger.warning(f"Invalid prediction data format, retrying: {prediction_data}")
                retry_count += 1
                time.sleep(1)

        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "rate limit" in error_str or "429" in str(e):
                # Rate limit error - wait longer before retrying
                wait_time = 60 + (retry_count * 30)  # Exponential backoff
                logger.warning(f"Rate limit hit, waiting {wait_time} seconds before retry {retry_count + 1}/{max_retries}")
                time.sleep(wait_time)
                retry_count += 1
            else:
                logger.error(f"Error generating prediction content: {str(e)}")
                retry_count += 1
                time.sleep(5)

    logger.error(f"Failed to generate prediction content after {max_retries} retries")
    return None

def validate_prediction_data(data: Dict[str, Any]) -> bool:
    """
    Validate the prediction data format.

    Args:
        data: Prediction data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["title", "endTime", "description", "tags"]

    # Check required fields
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False

    # Validate tags
    if not isinstance(data["tags"], list) or len(data["tags"]) != 3:
        logger.warning(f"Tags must be a list of exactly 3 items, got: {data['tags']}")
        return False

    for tag in data["tags"]:
        if tag not in AVAILABLE_TAGS:
            logger.warning(f"Invalid tag: {tag}")
            return False

    # Validate endTime format
    try:
        # Simple check for ISO format
        if not data["endTime"].endswith("Z") or "T" not in data["endTime"]:
            logger.warning(f"Invalid endTime format: {data['endTime']}")
            return False
    except Exception:
        logger.warning(f"Invalid endTime: {data.get('endTime')}")
        return False

    return True

def process_article_with_llm(article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process an article with the LLM to generate prediction market content.

    Args:
        article_data: Article data dictionary

    Returns:
        Dictionary with prediction market content or None if processing failed
    """
    try:
        # Try using LangChain first
        try:
            from langchain_integration import generate_prediction_market
            logger.info("Using LangChain for prediction market generation")
            prediction_data = generate_prediction_market(article_data, AVAILABLE_TAGS)
            if prediction_data:
                return prediction_data
            logger.warning("LangChain generation failed, falling back to direct API")
        except ImportError:
            logger.info("LangChain not available, using direct API")
        except Exception as e:
            logger.warning(f"Error using LangChain: {str(e)}, falling back to direct API")

        # Fall back to direct API if LangChain fails
        model = initialize_llm()
        prediction_data = generate_prediction_content(model, article_data)

        if prediction_data:
            # Add the original article data
            prediction_data["article"] = {
                "title": article_data["title"],
                "link": article_data["link"],
                "published_date": article_data["published_date"],
                "source": article_data["source"],
                "category": article_data["category"]
            }

            return prediction_data

        return None
    except Exception as e:
        logger.error(f"Error processing article with LLM: {str(e)}")
        return None
