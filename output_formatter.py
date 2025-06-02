"""
Output Formatter module.
Handles formatting processed data into the required JSON structure.
"""
import json
import logging
import uuid
import os
from typing import Dict, Any, List
from datetime import datetime, timezone
from config import OUTPUT_CONFIG
from strapi_service import strapi_service

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
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"Output saved to {filename}")

        # Send to Prediction Markets API if configured
        if strapi_service.is_configured():
            markets = output.get("eventsData", [{}])[0].get("markets", [])
            if markets:
                logger.info(f"Sending {len(markets)} markets to Prediction Markets API")

                # Check API health first
                is_healthy, health_message = strapi_service.check_api_health()
                if not is_healthy:
                    logger.warning(f"API health check failed: {health_message}")
                    logger.warning("Will attempt to send markets anyway with retry logic")

                # Try to send markets with retry logic
                successful = strapi_service.send_markets(markets, retry_on_error=True)

                if successful:
                    logger.info(f"Successfully sent {len(successful)} out of {len(markets)} markets to Prediction Markets API")
                else:
                    logger.error("Failed to send any markets to Prediction Markets API")

                    # Save failed markets to a backup file for later retry
                    backup_file = f"{os.path.splitext(filename)[0]}_failed_api_send.json"
                    try:
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            json.dump({"markets": markets}, f, indent=2, ensure_ascii=False)
                        logger.info(f"Saved failed markets to backup file: {backup_file}")
                        logger.info(f"You can retry sending these markets later when the API is available")
                    except Exception as e:
                        logger.error(f"Error saving backup file: {str(e)}")
            else:
                logger.warning("No markets found to send to Prediction Markets API")
        else:
            logger.info("Prediction Markets API integration not configured, skipping")

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
