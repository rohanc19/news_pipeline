"""
Output Formatter module.
Handles formatting processed data into the required JSON structure.
"""
import json
import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from config import OUTPUT_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_market_id() -> str:
    """
    Generate a unique market ID.
    
    Returns:
        Unique market ID string
    """
    return f"market_{uuid.uuid4().hex[:8]}"

def create_market_object(prediction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a market object from prediction data.
    
    Args:
        prediction_data: Prediction data from LLM
        
    Returns:
        Market object dictionary
    """
    # Get current time in ISO format
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Extract article data
    article = prediction_data.get("article", {})
    
    # Create market object
    market = {
        "id": generate_market_id(),
        "title": prediction_data["title"],
        "description": prediction_data["description"],
        "category": article.get("category", "Uncategorized"),
        "tags": prediction_data["tags"],
        "status": "open",
        "createdAt": current_time,
        "startTime": current_time,
        "endTime": prediction_data["endTime"],
        "resolutionTime": prediction_data["endTime"],  # Same as endTime for simplicity
        "result": None,
        "yesCount": OUTPUT_CONFIG["initial_yes_count"],
        "noCount": OUTPUT_CONFIG["initial_no_count"],
        "totalVolume": OUTPUT_CONFIG["initial_yes_count"] + OUTPUT_CONFIG["initial_no_count"],
        "currentYesProbability": 0.5,
        "currentNoProbability": 0.5,
        "creatorId": OUTPUT_CONFIG["creator_id"],
        "resolutionSource": article.get("link", "")
    }
    
    return market

def format_markets_by_category(markets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group markets by category.
    
    Args:
        markets: List of market objects
        
    Returns:
        Dictionary with markets grouped by category
    """
    markets_by_category = {}
    
    for market in markets:
        category = market["category"]
        if category not in markets_by_category:
            markets_by_category[category] = []
        
        markets_by_category[category].append(market)
    
    return markets_by_category

def format_final_output(markets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format the final output JSON.
    
    Args:
        markets: List of market objects
        
    Returns:
        Final output JSON structure
    """
    # Create the final output structure
    output = {
        "eventsData": [
            {
                "markets": markets
            }
        ]
    }
    
    return output

def save_output_to_file(output: Dict[str, Any], filename: str = OUTPUT_CONFIG["output_file"]) -> None:
    """
    Save the output to a JSON file.
    
    Args:
        output: Output dictionary
        filename: Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"Output saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving output to file: {str(e)}")

def get_markets_summary(markets: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get a summary of markets by category.
    
    Args:
        markets: List of market objects
        
    Returns:
        Dictionary with count of markets by category
    """
    summary = {}
    
    for market in markets:
        category = market["category"]
        if category not in summary:
            summary[category] = 0
        
        summary[category] += 1
    
    return summary
