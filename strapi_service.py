"""
Prediction Markets API Service module.
Handles sending prediction market data to the Prediction Markets API.
"""
import logging
import requests
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StrapiService:
    """Service for interacting with the Prediction Markets API."""

    def __init__(self):
        """Initialize the Prediction Markets API service with Strapi CMS URL."""
        # Strapi CMS URL
        self.api_url = "https://prediction-markets-strapi.onrender.com"
        # Your Strapi API token
        self.api_token = "c3ee4528f1a962949b1fecd2378a3090372a2b8f91557c877dc15be77621205782a06c7d233977f7bdd570e71893ca06f359f68faf6bc27793336d1846628e267449d3d30279e5bbc17916bad6cb1091a84203bf12546e269590b98de95da35ef12a963057e3d784dfffca1758d4a9a0ef74f3e239a70a261a9c939e44bdd7b1"
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.timeout = 10  # seconds

        logger.info(f"Strapi CMS service initialized with URL: {self.api_url}")

        # Set up headers with API token for authentication
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }

    def is_configured(self) -> bool:
        """Check if the Strapi CMS is properly configured."""
        return bool(self.api_url) and bool(self.api_token)

    def check_api_health(self) -> Tuple[bool, str]:
        """
        Check if the Strapi CMS is up and running.

        Returns:
            Tuple of (is_healthy, message)
        """
        try:
            # Use the Strapi health endpoint
            health_endpoint = f"{self.api_url}/_health"

            # Try the health endpoint first
            try:
                response = requests.get(
                    health_endpoint,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return True, "Strapi CMS is healthy"
            except:
                # If health endpoint fails, try the main URL
                pass

            # Fallback to checking the main URL
            response = requests.get(
                self.api_url,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return True, "Strapi CMS is healthy"
            else:
                return False, f"Strapi CMS returned status code: {response.status_code}"

        except requests.exceptions.RequestException as e:
            return False, f"Strapi CMS health check failed: {str(e)}"

        except Exception as e:
            return False, f"Unexpected error during Strapi CMS health check: {str(e)}"

    def send_market(self, market_data: Dict[str, Any], retry_on_error: bool = True) -> Optional[Dict[str, Any]]:
        """
        Send a single prediction market to the Strapi CMS.

        Args:
            market_data: Prediction market data
            retry_on_error: Whether to retry on error

        Returns:
            Response from the API or None if sending failed
        """
        if not self.is_configured():
            logger.error("Strapi CMS URL is not configured. Cannot send market data.")
            return None

        # Check API health first
        is_healthy, health_message = self.check_api_health()
        if not is_healthy:
            logger.warning(f"Strapi CMS health check failed: {health_message}")
            if not retry_on_error:
                return None
            # Continue anyway if retry_on_error is True

        # Format the market data for Strapi
        strapi_data = self._format_market_for_strapi(market_data)

        # Retry logic
        retries = 0
        while retries <= self.max_retries:
            try:
                # Send the data to Strapi
                endpoint = f"{self.api_url}/api/prediction-markets"

                if retries > 0:
                    logger.info(f"Retry attempt {retries}/{self.max_retries} for market '{market_data['title']}'")

                # Prepare the request payload according to Strapi's API format
                payload = {"data": strapi_data}

                response = requests.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )

                response.raise_for_status()
                logger.info(f"Successfully sent market '{market_data['title']}' to Strapi CMS")

                return response.json()

            except requests.exceptions.RequestException as e:
                logger.error(f"Error sending market to Strapi CMS: {str(e)}")
                if hasattr(e, 'response') and e.response:
                    logger.error(f"Response: {e.response.text[:200]}...")

                # Determine if we should retry
                if not retry_on_error or retries >= self.max_retries:
                    return None

                retries += 1
                logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                time.sleep(self.retry_delay)

            except Exception as e:
                logger.error(f"Unexpected error sending market to Strapi CMS: {str(e)}")

                # Determine if we should retry
                if not retry_on_error or retries >= self.max_retries:
                    return None

                retries += 1
                logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                time.sleep(self.retry_delay)

        return None

    def send_markets(self, markets: List[Dict[str, Any]], retry_on_error: bool = True) -> List[Dict[str, Any]]:
        """
        Send multiple prediction markets to the Prediction Markets API.

        Args:
            markets: List of prediction market data
            retry_on_error: Whether to retry on error

        Returns:
            List of successful responses from the API
        """
        if not self.is_configured():
            logger.error("Strapi CMS URL is not configured. Cannot send market data.")
            return []

        # First check API health
        is_healthy, health_message = self.check_api_health()
        if not is_healthy:
            logger.warning(f"API health check failed before batch send: {health_message}")
            if not retry_on_error:
                logger.error("Skipping batch send due to API health check failure")
                return []
            logger.warning("Continuing with batch send despite API health check failure")

        successful_responses = []
        failed_markets = []

        # Process markets in batches to avoid overwhelming the API
        batch_size = 5
        total_markets = len(markets)

        logger.info(f"Sending {total_markets} markets to Strapi CMS")

        for i in range(0, total_markets, batch_size):
            batch = markets[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_markets + batch_size - 1)//batch_size} ({len(batch)} markets)")

            for market in batch:
                try:
                    response = self.send_market(market, retry_on_error=retry_on_error)
                    if response:
                        successful_responses.append(response)
                    else:
                        failed_markets.append(market)
                        logger.warning(f"Failed to send market: {market.get('title', 'Unknown title')}")
                except Exception as e:
                    failed_markets.append(market)
                    logger.error(f"Unexpected error in batch send: {str(e)}")

            # Add a small delay between batches to avoid rate limiting
            if i + batch_size < total_markets:
                time.sleep(1)

        success_rate = len(successful_responses) / total_markets * 100 if total_markets > 0 else 0
        logger.info(f"Successfully sent {len(successful_responses)} out of {total_markets} markets to Strapi CMS ({success_rate:.1f}%)")

        if failed_markets:
            logger.warning(f"Failed to send {len(failed_markets)} markets")

        return successful_responses

    def _format_market_for_strapi(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format market data for the Strapi CMS.

        Args:
            market_data: Prediction market data

        Returns:
            Formatted data for the Strapi API
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
