"""
Strapi Service module.
Handles sending prediction market data to Strapi CMS.
"""
import os
import logging
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StrapiService:
    """Service for interacting with Strapi CMS."""
    
    def __init__(self):
        """Initialize the Strapi service with configuration from environment variables."""
        self.api_url = os.getenv("STRAPI_API_URL")
        self.api_token = os.getenv("STRAPI_API_TOKEN")
        
        if not self.api_url:
            logger.warning("STRAPI_API_URL environment variable not set")
        
        if not self.api_token:
            logger.warning("STRAPI_API_TOKEN environment variable not set")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}" if self.api_token else ""
        }
    
    def is_configured(self) -> bool:
        """Check if Strapi is properly configured."""
        return bool(self.api_url and self.api_token)
    
    def send_market(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a single prediction market to Strapi.
        
        Args:
            market_data: Prediction market data
            
        Returns:
            Response from Strapi or None if sending failed
        """
        if not self.is_configured():
            logger.error("Strapi is not properly configured. Cannot send market data.")
            return None
        
        try:
            # Format the market data for Strapi
            strapi_data = self._format_market_for_strapi(market_data)
            
            # Send the data to Strapi
            endpoint = f"{self.api_url}/api/prediction-markets"
            response = requests.post(
                endpoint,
                headers=self.headers,
                json={"data": strapi_data}
            )
            
            response.raise_for_status()
            logger.info(f"Successfully sent market '{market_data['title']}' to Strapi")
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending market to Strapi: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error sending market to Strapi: {str(e)}")
            return None
    
    def send_markets(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Send multiple prediction markets to Strapi.
        
        Args:
            markets: List of prediction market data
            
        Returns:
            List of successful responses from Strapi
        """
        if not self.is_configured():
            logger.error("Strapi is not properly configured. Cannot send market data.")
            return []
        
        successful_responses = []
        
        for market in markets:
            response = self.send_market(market)
            if response:
                successful_responses.append(response)
        
        logger.info(f"Successfully sent {len(successful_responses)} out of {len(markets)} markets to Strapi")
        
        return successful_responses
    
    def _format_market_for_strapi(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format market data for Strapi.
        
        Args:
            market_data: Prediction market data
            
        Returns:
            Formatted data for Strapi
        """
        # Convert the market data to the format expected by Strapi
        # Adjust this based on your Strapi content type structure
        formatted_data = {
            "title": market_data["title"],
            "description": market_data["description"],
            "category": market_data["category"],
            "tags": market_data.get("tags", []),
            "status": market_data.get("status", "open"),
            "createdAt": market_data.get("createdAt", datetime.now().isoformat()),
            "endTime": market_data.get("endTime"),
            "resolutionTime": market_data.get("resolutionTime"),
            "yesCount": market_data.get("yesCount", 0),
            "noCount": market_data.get("noCount", 0),
            "currentYesProbability": market_data.get("currentYesProbability", 0.5),
            "currentNoProbability": market_data.get("currentNoProbability", 0.5),
            "resolutionSource": market_data.get("resolutionSource", ""),
            "externalId": market_data.get("id", "")
        }
        
        return formatted_data

# Create a singleton instance
strapi_service = StrapiService()
