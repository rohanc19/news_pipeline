"""
Main Pipeline module.
Orchestrates the entire news processing pipeline.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from tqdm import tqdm
import concurrent.futures
from datetime import datetime

from config import RSS_FEEDS, PIPELINE_CONFIG
from feed_parser import process_feed
from article_processor import enrich_article_data
from llm_service import process_article_with_llm
from output_formatter import (
    create_market_object, 
    format_final_output, 
    save_output_to_file,
    get_markets_summary
)
from utils import (
    setup_logging,
    deduplicate_markets,
    limit_markets_per_category,
    save_checkpoint,
    load_checkpoint,
    ensure_directory_exists
)

# Set up logging
logger = setup_logging()

def process_article(article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process a single article through the pipeline.
    
    Args:
        article_data: Article data dictionary
        
    Returns:
        Market object or None if processing failed
    """
    try:
        # Enrich article with full content
        enriched_article = enrich_article_data(article_data)
        
        # Process with LLM
        prediction_data = process_article_with_llm(enriched_article)
        
        if prediction_data:
            # Create market object
            market = create_market_object(prediction_data)
            return market
        
        return None
    except Exception as e:
        logger.error(f"Error processing article {article_data.get('title', 'Unknown')}: {str(e)}")
        return None

def process_category(category: str, feed_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process all feeds for a category.
    
    Args:
        category: Category name
        feed_configs: List of feed configurations for the category
        
    Returns:
        List of market objects
    """
    logger.info(f"Processing category: {category}")
    
    all_articles = []
    markets = []
    
    # Process each feed in the category
    for feed_config in feed_configs:
        articles = process_feed(feed_config)
        all_articles.extend(articles)
    
    logger.info(f"Found {len(all_articles)} articles for category {category}")
    
    # Process articles in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all articles for processing
        future_to_article = {
            executor.submit(process_article, article): article 
            for article in all_articles
        }
        
        # Process results as they complete
        for future in tqdm(
            concurrent.futures.as_completed(future_to_article), 
            total=len(future_to_article),
            desc=f"Processing {category} articles"
        ):
            article = future_to_article[future]
            try:
                market = future.result()
                if market:
                    markets.append(market)
            except Exception as e:
                logger.error(f"Error processing article {article.get('title', 'Unknown')}: {str(e)}")
    
    # Deduplicate markets
    unique_markets = deduplicate_markets(markets)
    
    # Limit markets per category
    limited_markets = unique_markets[:PIPELINE_CONFIG["markets_per_category"]]
    
    logger.info(f"Generated {len(limited_markets)} markets for category {category}")
    
    return limited_markets

def run_pipeline() -> Dict[str, Any]:
    """
    Run the entire pipeline.
    
    Returns:
        Final output dictionary
    """
    start_time = time.time()
    logger.info("Starting news pipeline")
    
    # Create checkpoints directory
    ensure_directory_exists("checkpoints")
    
    # Group feeds by category
    feeds_by_category = {}
    for feed in RSS_FEEDS:
        if feed.category not in feeds_by_category:
            feeds_by_category[feed.category] = []
        feeds_by_category[feed.category].append(feed)
    
    all_markets = []
    
    # Process each category
    for category, feeds in feeds_by_category.items():
        # Check for checkpoint
        checkpoint_file = f"checkpoints/{category.lower().replace(' & ', '_').replace(' ', '_')}.json"
        checkpoint_data = load_checkpoint(checkpoint_file)
        
        if checkpoint_data:
            logger.info(f"Loaded {len(checkpoint_data)} markets from checkpoint for {category}")
            all_markets.extend(checkpoint_data)
        else:
            # Process category
            markets = process_category(category, feeds)
            
            # Save checkpoint
            save_checkpoint(markets, checkpoint_file)
            
            all_markets.extend(markets)
    
    # Deduplicate across all categories
    unique_markets = deduplicate_markets(all_markets)
    
    # Limit markets per category
    limited_markets = limit_markets_per_category(
        unique_markets, 
        PIPELINE_CONFIG["markets_per_category"]
    )
    
    # Format final output
    output = format_final_output(limited_markets)
    
    # Save output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"prediction_markets_{timestamp}.json"
    save_output_to_file(output, output_file)
    
    # Log summary
    summary = get_markets_summary(limited_markets)
    logger.info(f"Markets summary: {summary}")
    
    end_time = time.time()
    logger.info(f"Pipeline completed in {end_time - start_time:.2f} seconds")
    
    return output
