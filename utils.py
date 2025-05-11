"""
Utilities module.
Contains helper functions used across the pipeline.
"""
import logging
import os
import json
from typing import Dict, Any, List, Set
import hashlib
from datetime import datetime

# Configure logging
def setup_logging(log_level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('news_pipeline.log')
        ]
    )
    
    # Reduce verbosity of some loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured")
    
    return logger

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging.info(f"Created directory: {directory_path}")

def generate_content_hash(content: str) -> str:
    """
    Generate a hash of content to identify duplicates.
    
    Args:
        content: Content to hash
        
    Returns:
        Hash string
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def deduplicate_markets(markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate markets based on title similarity.
    
    Args:
        markets: List of market objects
        
    Returns:
        Deduplicated list of market objects
    """
    unique_markets = []
    seen_titles = set()
    seen_hashes = set()
    
    for market in markets:
        # Generate a normalized version of the title for comparison
        normalized_title = market["title"].lower().strip()
        title_hash = generate_content_hash(normalized_title)
        
        # Generate a hash of the description for additional deduplication
        description_hash = generate_content_hash(market["description"])
        
        # Check if we've seen this title or a very similar one
        if title_hash not in seen_hashes and description_hash not in seen_hashes:
            unique_markets.append(market)
            seen_titles.add(normalized_title)
            seen_hashes.add(title_hash)
            seen_hashes.add(description_hash)
    
    logging.info(f"Deduplicated {len(markets) - len(unique_markets)} markets")
    return unique_markets

def limit_markets_per_category(markets: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """
    Limit the number of markets per category.
    
    Args:
        markets: List of market objects
        limit: Maximum number of markets per category
        
    Returns:
        Limited list of market objects
    """
    markets_by_category = {}
    limited_markets = []
    
    # Group markets by category
    for market in markets:
        category = market["category"]
        if category not in markets_by_category:
            markets_by_category[category] = []
        
        markets_by_category[category].append(market)
    
    # Limit each category
    for category, category_markets in markets_by_category.items():
        limited_markets.extend(category_markets[:limit])
        
        if len(category_markets) > limit:
            logging.info(f"Limited {category} markets from {len(category_markets)} to {limit}")
    
    return limited_markets

def save_checkpoint(data: Any, filename: str) -> None:
    """
    Save a checkpoint of data to a file.
    
    Args:
        data: Data to save
        filename: Filename to save to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Checkpoint saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving checkpoint: {str(e)}")

def load_checkpoint(filename: str) -> Any:
    """
    Load a checkpoint from a file.
    
    Args:
        filename: Filename to load from
        
    Returns:
        Loaded data or None if file doesn't exist
    """
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"Checkpoint loaded from {filename}")
        return data
    except Exception as e:
        logging.error(f"Error loading checkpoint: {str(e)}")
        return None
