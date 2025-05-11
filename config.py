"""
Configuration module for the news pipeline.
Contains RSS feed URLs, LLM settings, and other configuration parameters.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

# RSS Feed Configuration
class FeedConfig(BaseModel):
    url: str
    category: str
    fallback_urls: Optional[List[str]] = None

# List of RSS feeds with their categories
RSS_FEEDS = [
    # Politics
    FeedConfig(url="https://feeds.feedburner.com/ndtvnews-india-news", category="Politics"),

    # Culture
    FeedConfig(url="https://www.rollingstone.com/culture/feed/", category="Culture"),

    # Crypto
    FeedConfig(url="https://cointelegraph.com/rss", category="Crypto"),

    # Economics
    FeedConfig(url="https://www.livemint.com/rss/economy", category="Economics"),

    # Companies
    FeedConfig(url="https://techcrunch.com/feed/", category="Companies"),

    # World
    FeedConfig(url="https://www.aljazeera.com/xml/rss/all.xml", category="World"),

    # Additional working feeds
    FeedConfig(url="https://rss.nytimes.com/services/xml/rss/nyt/World.xml", category="World"),
    FeedConfig(url="https://feeds.bbci.co.uk/news/world/rss.xml", category="World"),
    FeedConfig(url="https://www.theguardian.com/world/rss", category="World"),

    FeedConfig(url="https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", category="Tech & Science"),
    FeedConfig(url="https://feeds.wired.com/wired/index", category="Tech & Science"),

    FeedConfig(url="https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", category="Companies"),

    FeedConfig(url="https://www.economist.com/finance-and-economics/rss.xml", category="Economics"),
]

# Available tags for market categorization
AVAILABLE_TAGS = [
    "Politics", "Sports", "Business", "Finance", "Entertainment", "Technology", "Science", "Health",
    "World Affairs", "Climate", "Crypto", "Economy", "Companies", "Consumer Trends", "Travel",
    "Education", "Energy", "Environment", "Weather", "Law", "Government", "Elections", "Stock Market",
    "Startups", "Public Figures", "Awards", "Festivals", "Innovation", "Gadgets", "Artificial Intelligence",
    "Space", "Mergers & Acquisitions", "Real Estate", "Agriculture", "Food & Beverage", "Defense & Military",
    "Currency", "Trade", "Pandemics", "Employment", "Media & News", "Transportation", "Social Media Trends",
    "IPOs", "Court Cases", "Natural Disasters", "Religion", "International Relations", "Diplomacy", "Conflict"
]

# LLM Configuration
LLM_CONFIG = {
    "model": "gemini-1.5-flash",  # or equivalent model
    "temperature": 0.2,
    "max_output_tokens": 1024,
    "top_p": 0.95,
    "top_k": 40,
}

# Pipeline Configuration
PIPELINE_CONFIG = {
    "recent_days": 5,  # Articles from the past 5 days
    "markets_per_category": 30,  # 30 unique markets per category
    "max_retries": 3,  # Maximum retries for API calls
    "timeout": 30,  # Timeout for HTTP requests in seconds
}

# Output Configuration
OUTPUT_CONFIG = {
    "output_file": "prediction_markets.json",
    "creator_id": "kalshi-generator",
    "initial_yes_count": 50000,
    "initial_no_count": 50000,
}
