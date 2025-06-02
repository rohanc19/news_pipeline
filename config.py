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

# List of RSS feeds with their categories (tested and working feeds only)
RSS_FEEDS = [
    # TRENDING - Major breaking news sources (2/3 working)
    FeedConfig(url="https://feeds.bbci.co.uk/news/rss.xml", category="Trending"),
    FeedConfig(url="https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms", category="Trending"),

    # POLITICS - Indian and international political news (2/3 working)
    FeedConfig(url="https://www.thehindu.com/news/national/feeder/default.rss", category="Politics"),
    FeedConfig(url="https://indianexpress.com/section/india/feed/", category="Politics"),

    # ECONOMY - Economic and financial news (2/3 working)
    FeedConfig(url="https://economictimes.indiatimes.com/rssfeedstopstories.cms", category="Economy"),
    FeedConfig(url="https://www.business-standard.com/rss/economy-policy-104.rss", category="Economy"),

    # CRYPTO - Cryptocurrency news (3/3 working - 100% success!)
    FeedConfig(url="https://cointelegraph.com/rss", category="Crypto"),
    FeedConfig(url="https://coindesk.com/arc/outboundfeeds/rss/", category="Crypto"),
    FeedConfig(url="https://decrypt.co/feed", category="Crypto"),

    # TECH - Technology news (2/4 working)
    FeedConfig(url="https://techcrunch.com/feed/", category="Tech"),
    FeedConfig(url="https://www.wired.com/feed/rss", category="Tech"),

    # WORLD - International news (2/3 working)
    FeedConfig(url="https://feeds.bbci.co.uk/news/world/rss.xml", category="World"),
    FeedConfig(url="https://www.aljazeera.com/xml/rss/all.xml", category="World"),

    # CULTURE - Entertainment and cultural news (2/3 working)
    FeedConfig(url="https://www.rollingstone.com/music/feed/", category="Culture"),
    FeedConfig(url="https://variety.com/feed/", category="Culture"),

    # SPORTS - Sports news (3/3 working - 100% success!)
    FeedConfig(url="https://feeds.bbci.co.uk/sport/rss.xml", category="Sports"),
    FeedConfig(url="https://www.espn.com/espn/rss/news", category="Sports"),
    FeedConfig(url="https://timesofindia.indiatimes.com/rssfeeds/4719148.cms", category="Sports"),

    # EDUCATION - Educational news and updates (2/3 working)
    FeedConfig(url="https://www.thehindu.com/education/feeder/default.rss", category="Education"),
    FeedConfig(url="https://indianexpress.com/section/education/feed/", category="Education"),

    # BUSINESS - Business and corporate news (2/3 working)
    FeedConfig(url="https://economictimes.indiatimes.com/rssfeedstopstories.cms", category="Business"),
    FeedConfig(url="https://www.business-standard.com/rss/companies-101.rss", category="Business"),

    # ENVIRONMENT - Environmental and climate news (1/3 working)
    FeedConfig(url="https://www.theguardian.com/environment/rss", category="Environment"),
    # Adding backup environment feeds
    FeedConfig(url="https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", category="Environment"),
]

# Available tags for market categorization (updated with new subcategories)
AVAILABLE_TAGS = [
    # Trending subcategories
    "Breaking News", "Lok Sabha Elections", "IPL 2025", "Budget 2025", "Startup News", "Geopolitics",
    "Stock Market", "Crypto Prices", "India vs Pakistan", "AI in India", "Weather Alerts", "Bollywood",
    "South Cinema", "New Parliament", "NEET/JEE Updates",

    # Politics subcategories
    "State Elections", "Cabinet Decisions", "Parliament Sessions", "Policies and Bills", "Supreme Court",
    "Election Commission", "Opposition Updates", "PM Modi", "India-US Relations", "India-China Tensions",

    # Economy subcategories
    "RBI Announcements", "Budget", "GST & Taxes", "Inflation", "Unemployment", "Banking Sector",
    "Startup Funding", "Forex & Trade", "Real Estate",

    # Crypto subcategories
    "Bitcoin", "Ethereum", "Memecoins", "Crypto Regulations India", "RBI on Crypto", "Crypto Scams",
    "Stablecoins", "Airdrops", "NFTs",

    # Tech subcategories
    "AI", "ISRO Launches", "Startups", "Government Apps", "Cybersecurity", "Meta vs Competition",
    "Space Missions", "5G Rollout", "ONDC", "Digital India",

    # World subcategories
    "Middle East Conflict", "Global Elections", "Russia-Ukraine War", "China-Taiwan", "UN Updates",
    "US Politics", "Africa Development", "Climate Agreements", "Pakistan Crisis",

    # Culture subcategories
    "Tollywood", "Celebrity Gossip", "Music Awards", "Reality TV", "Viral Trends", "Social Media Buzz",
    "Memes", "OTT Shows", "Religion & Festivals",

    # Sports subcategories
    "Cricket", "IPL", "Indian Football", "Olympics", "Kabaddi League", "Chess", "Badminton",
    "Wrestling", "Formula 1", "World Cup",

    # Education subcategories
    "NEET", "JEE", "CBSE Board", "UPSC", "UGC-NET", "Study Abroad", "Govt Jobs", "Online Courses",
    "Scholarships",

    # Business subcategories
    "Tata", "Reliance", "Adani", "Startup Acquisitions", "IPO News", "FMCG", "Automobiles",
    "Tech Giants", "E-commerce",

    # Environment subcategories
    "Air Pollution", "Water Crisis", "Wildlife", "Climate Change", "Heatwaves", "Recycling",
    "Forest Fires", "Plastic Ban",

    # General categories (keeping some original ones for compatibility)
    "Politics", "Sports", "Business", "Finance", "Entertainment", "Technology", "Science", "Health",
    "World Affairs", "Climate", "Crypto", "Economy", "Education", "Environment"
]

# Category structure for prediction markets
CATEGORY_STRUCTURE = {
    "Trending": {
        "subcategories": [
            "All", "Breaking News", "Lok Sabha Elections", "IPL 2025", "Budget 2025", "Startup News",
            "Geopolitics", "Stock Market", "Crypto Prices", "India vs Pakistan", "AI in India",
            "Weather Alerts", "Bollywood", "South Cinema", "New Parliament", "NEET/JEE Updates"
        ]
    },
    "Politics": {
        "subcategories": [
            "All", "Lok Sabha Elections", "State Elections", "Cabinet Decisions", "Parliament Sessions",
            "Policies and Bills", "Supreme Court", "Election Commission", "Opposition Updates", "PM Modi",
            "Geopolitics", "India-US Relations", "India-China Tensions"
        ]
    },
    "Economy": {
        "subcategories": [
            "All", "RBI Announcements", "Budget", "Stock Market", "GST & Taxes", "Inflation",
            "Unemployment", "Banking Sector", "Startup Funding", "Forex & Trade", "Real Estate"
        ]
    },
    "Crypto": {
        "subcategories": [
            "All", "Bitcoin", "Ethereum", "Memecoins", "Crypto Regulations India", "RBI on Crypto",
            "Crypto Scams", "Stablecoins", "Airdrops", "NFTs"
        ]
    },
    "Tech": {
        "subcategories": [
            "All", "AI", "ISRO Launches", "Startups", "Government Apps", "Cybersecurity",
            "Meta vs Competition", "Space Missions", "5G Rollout", "ONDC", "Digital India"
        ]
    },
    "World": {
        "subcategories": [
            "All", "Middle East Conflict", "Global Elections", "Russia-Ukraine War", "China-Taiwan",
            "UN Updates", "US Politics", "Africa Development", "Climate Agreements", "Pakistan Crisis"
        ]
    },
    "Culture": {
        "subcategories": [
            "All", "Bollywood", "Tollywood", "Celebrity Gossip", "Music Awards", "Reality TV",
            "Viral Trends", "Social Media Buzz", "Memes", "OTT Shows", "Religion & Festivals"
        ]
    },
    "Sports": {
        "subcategories": [
            "All", "Cricket", "IPL", "Indian Football", "Olympics", "Kabaddi League", "Chess",
            "Badminton", "Wrestling", "Formula 1", "World Cup"
        ]
    },
    "Education": {
        "subcategories": [
            "All", "NEET", "JEE", "CBSE Board", "UPSC", "UGC-NET", "Study Abroad", "Govt Jobs",
            "Online Courses", "Scholarships"
        ]
    },
    "Business": {
        "subcategories": [
            "All", "Tata", "Reliance", "Adani", "Startup Acquisitions", "IPO News", "FMCG",
            "Automobiles", "Tech Giants", "E-commerce"
        ]
    },
    "Environment": {
        "subcategories": [
            "All", "Air Pollution", "Water Crisis", "Wildlife", "Climate Change", "Heatwaves",
            "Recycling", "Forest Fires", "Plastic Ban"
        ]
    }
}

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
    "recent_days": 7,  # Articles from the past 7 days (more articles)
    "markets_per_category": 30,  # 30 markets per category as requested
    "max_retries": 3,  # Maximum retries for API calls
    "timeout": 30,  # Timeout for HTTP requests in seconds
    "rate_limit_delay": 4.5,  # Delay between API calls (seconds) for free tier (15 req/min = 4s interval)
    "max_concurrent_workers": 1,  # Sequential processing for free tier
}

# Output Configuration
OUTPUT_CONFIG = {
    "output_file": "prediction_markets.json",
    "creator_id": "kalshi-generator",
    "initial_yes_count": 50000,
    "initial_no_count": 50000,
}
