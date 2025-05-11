"""
Article Processor module.
Handles fetching full article content and extracting key information.
"""
import requests
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import time
from config import PIPELINE_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_article_content(url: str, timeout: int = PIPELINE_CONFIG["timeout"]) -> Optional[str]:
    """
    Fetch the full content of an article from its URL.
    
    Args:
        url: URL of the article
        timeout: Timeout for the HTTP request in seconds
        
    Returns:
        HTML content of the article or None if fetching failed
    """
    try:
        logger.info(f"Fetching article content from {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching article {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching article {url}: {str(e)}")
        return None

def extract_article_text(html_content: str) -> str:
    """
    Extract the main text content from an article's HTML.
    
    Args:
        html_content: HTML content of the article
        
    Returns:
        Extracted text content
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from HTML: {str(e)}")
        return ""

def clean_article_text(text: str, max_length: int = 8000) -> str:
    """
    Clean and prepare article text for LLM processing.
    
    Args:
        text: Raw article text
        max_length: Maximum length of text to return
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def enrich_article_data(article_data: Dict[str, Any], max_retries: int = PIPELINE_CONFIG["max_retries"]) -> Dict[str, Any]:
    """
    Enrich article data with full content if available.
    
    Args:
        article_data: Article data dictionary
        max_retries: Maximum number of retries for fetching the article
        
    Returns:
        Enriched article data dictionary
    """
    # If we already have content, use it
    if article_data.get("content") and len(article_data["content"]) > 500:
        article_data["processed_content"] = clean_article_text(article_data["content"])
        return article_data
    
    # Otherwise, try to fetch the full article
    retry_count = 0
    while retry_count < max_retries:
        html_content = fetch_article_content(article_data["link"])
        
        if html_content:
            article_text = extract_article_text(html_content)
            if article_text:
                article_data["processed_content"] = clean_article_text(article_text)
                return article_data
        
        retry_count += 1
        if retry_count < max_retries:
            logger.warning(f"Retrying article {article_data['link']} (attempt {retry_count+1}/{max_retries})")
            time.sleep(2)  # Wait before retrying
    
    # If we couldn't get the full content, use what we have
    logger.warning(f"Could not fetch full content for {article_data['link']}, using summary")
    article_data["processed_content"] = clean_article_text(article_data.get("summary", ""))
    
    return article_data
