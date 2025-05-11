"""
RSS Feed Parser module.
Handles fetching and parsing RSS feeds, extracting articles from the past N days.
"""
import feedparser
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser
import time
from config import FeedConfig, PIPELINE_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_feed(feed_url: str, timeout: int = PIPELINE_CONFIG["timeout"]) -> Optional[feedparser.FeedParserDict]:
    """
    Fetch an RSS feed from the given URL.

    Args:
        feed_url: URL of the RSS feed
        timeout: Timeout for the HTTP request in seconds

    Returns:
        Parsed feed or None if fetching failed
    """
    try:
        logger.info(f"Fetching feed from {feed_url}")
        response = requests.get(feed_url, timeout=timeout)
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        if not feed.entries:
            logger.warning(f"No entries found in feed: {feed_url}")
            return None

        return feed
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching feed {feed_url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing feed {feed_url}: {str(e)}")
        return None

def extract_date(entry: Dict[str, Any]) -> Optional[datetime]:
    """
    Extract the publication date from a feed entry.

    Args:
        entry: Feed entry dictionary

    Returns:
        Publication date as datetime object or None if not found
    """
    date_fields = ['published', 'pubDate', 'updated', 'date']

    for field in date_fields:
        if field in entry and entry[field]:
            try:
                return date_parser.parse(entry[field])
            except (ValueError, TypeError):
                continue

    logger.warning(f"Could not extract date from entry: {entry.get('title', 'Unknown title')}")
    return None

def filter_recent_articles(entries: List[Dict[str, Any]], days: int = PIPELINE_CONFIG["recent_days"]) -> List[Dict[str, Any]]:
    """
    Filter articles to only include those from the past N days.

    Args:
        entries: List of feed entries
        days: Number of days to look back

    Returns:
        Filtered list of recent entries
    """
    # Create a timezone-naive cutoff date
    cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=days)
    recent_entries = []

    for entry in entries:
        pub_date = extract_date(entry)
        if pub_date:
            # Make the pub_date timezone-naive for comparison
            if pub_date.tzinfo:
                pub_date = pub_date.replace(tzinfo=None)

            if pub_date >= cutoff_date:
                # Add the parsed date to the entry for later use
                entry['parsed_date'] = pub_date
                recent_entries.append(entry)

    logger.info(f"Filtered {len(recent_entries)} recent articles out of {len(entries)} total")
    return recent_entries

def extract_article_data(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant data from a feed entry.

    Args:
        entry: Feed entry dictionary

    Returns:
        Dictionary with extracted article data
    """
    # Get the published date, defaulting to current time if not available
    published_date = entry.get("parsed_date", datetime.now().replace(tzinfo=None))

    # Convert to string format to avoid timezone issues
    if isinstance(published_date, datetime):
        published_date_str = published_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        published_date_str = str(published_date)

    article_data = {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "summary": entry.get("summary", ""),
        "published_date": published_date_str,
        "source": entry.get("source", {}).get("title", "Unknown Source"),
    }

    # Try to get the full content if available
    if "content" in entry and entry["content"]:
        # Some feeds provide full content
        if isinstance(entry["content"], list) and len(entry["content"]) > 0:
            article_data["content"] = entry["content"][0].get("value", "")
        else:
            article_data["content"] = entry["content"]
    else:
        # Otherwise use the summary
        article_data["content"] = article_data["summary"]

    return article_data

def process_feed(feed_config: FeedConfig, max_retries: int = PIPELINE_CONFIG["max_retries"]) -> List[Dict[str, Any]]:
    """
    Process a feed and extract recent articles.

    Args:
        feed_config: Configuration for the feed
        max_retries: Maximum number of retries for fetching the feed

    Returns:
        List of article data dictionaries
    """
    articles = []
    retry_count = 0

    while retry_count < max_retries:
        feed = fetch_feed(feed_config.url)

        if feed and feed.entries:
            # Filter recent articles
            recent_entries = filter_recent_articles(feed.entries)

            # Extract article data
            for entry in recent_entries:
                article_data = extract_article_data(entry)
                article_data["category"] = feed_config.category
                articles.append(article_data)

            break

        retry_count += 1
        if retry_count < max_retries:
            logger.warning(f"Retrying feed {feed_config.url} (attempt {retry_count+1}/{max_retries})")
            time.sleep(2)  # Wait before retrying

    if not articles and feed_config.fallback_urls:
        logger.info(f"Using fallback URLs for {feed_config.category}")
        for fallback_url in feed_config.fallback_urls:
            fallback_feed = fetch_feed(fallback_url)
            if fallback_feed and fallback_feed.entries:
                recent_entries = filter_recent_articles(fallback_feed.entries)
                for entry in recent_entries:
                    article_data = extract_article_data(entry)
                    article_data["category"] = feed_config.category
                    articles.append(article_data)

                if articles:
                    break

    logger.info(f"Processed {len(articles)} articles from {feed_config.category} feed")
    return articles
