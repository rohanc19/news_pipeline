"""
Run the full pipeline to generate 30 prediction markets per category for all 11 categories.
Total target: 330 prediction markets.
"""
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

from config import RSS_FEEDS, PIPELINE_CONFIG, CATEGORY_STRUCTURE
from feed_parser import process_feed
from article_processor import enrich_article_data
from llm_service import process_article_with_llm
from output_formatter import create_market_object, format_final_output
from utils import setup_logging, deduplicate_markets, ensure_directory_exists

# Load environment variables
load_dotenv()

def run_comprehensive_pipeline():
    """Run the pipeline to generate 30 markets per category."""
    logger = setup_logging()
    logger.info("🚀 Starting comprehensive pipeline: 30 markets per category")
    
    start_time = time.time()
    
    # Create output directory
    ensure_directory_exists("outputs")
    
    # Group feeds by category
    feeds_by_category = {}
    for feed in RSS_FEEDS:
        if feed.category not in feeds_by_category:
            feeds_by_category[feed.category] = []
        feeds_by_category[feed.category].append(feed)
    
    all_markets = []
    category_stats = {}
    
    # Target categories (all 11)
    target_categories = list(CATEGORY_STRUCTURE.keys())
    
    logger.info(f"📊 Target: {len(target_categories)} categories × 30 markets = {len(target_categories) * 30} total markets")
    
    # Process each category
    for category_idx, category in enumerate(target_categories, 1):
        logger.info(f"\n🏷️  Processing Category {category_idx}/11: {category}")
        logger.info("=" * 60)
        
        category_markets = []
        category_stats[category] = {
            "target": 30,
            "articles_processed": 0,
            "markets_created": 0,
            "feeds_used": 0
        }
        
        # Get feeds for this category
        category_feeds = feeds_by_category.get(category, [])
        if not category_feeds:
            logger.warning(f"⚠️ No RSS feeds found for category: {category}")
            continue
        
        logger.info(f"📡 Available feeds: {len(category_feeds)}")
        
        # Process feeds until we get 30 markets
        for feed_idx, feed in enumerate(category_feeds):
            if len(category_markets) >= 30:
                break
                
            logger.info(f"\n📰 Feed {feed_idx + 1}/{len(category_feeds)}: {feed.url}")
            
            try:
                # Get articles from feed
                articles = process_feed(feed)
                logger.info(f"   📄 Found {len(articles)} articles")
                
                if not articles:
                    continue
                
                category_stats[category]["feeds_used"] += 1
                
                # Process articles from this feed
                for article_idx, article in enumerate(articles):
                    if len(category_markets) >= 30:
                        break
                    
                    try:
                        logger.info(f"   📝 Processing article {article_idx + 1}: {article.get('title', 'Unknown')[:50]}...")
                        
                        # Enrich article
                        enriched_article = enrich_article_data(article)
                        category_stats[category]["articles_processed"] += 1
                        
                        # Process with LLM
                        prediction_data = process_article_with_llm(enriched_article)
                        
                        if prediction_data:
                            # Create market object
                            market = create_market_object(prediction_data)
                            category_markets.append(market)
                            category_stats[category]["markets_created"] += 1
                            
                            logger.info(f"   ✅ Market {len(category_markets)}/30 created: {market.get('title', 'Unknown')[:50]}...")
                        else:
                            logger.warning(f"   ❌ Failed to create market for article")
                        
                        # Rate limiting delay
                        if len(category_markets) < 30:  # Don't delay after the last one
                            delay = PIPELINE_CONFIG.get("rate_limit_delay", 4.5)
                            logger.info(f"   ⏳ Rate limit delay: {delay}s")
                            time.sleep(delay)
                            
                    except Exception as e:
                        logger.error(f"   ❌ Error processing article: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"❌ Error processing feed {feed.url}: {str(e)}")
                continue
        
        # Deduplicate markets for this category
        unique_category_markets = deduplicate_markets(category_markets)
        
        # Limit to exactly 30 markets
        final_category_markets = unique_category_markets[:30]
        
        logger.info(f"\n📊 Category {category} Summary:")
        logger.info(f"   🎯 Target: 30 markets")
        logger.info(f"   ✅ Created: {len(final_category_markets)} markets")
        logger.info(f"   📰 Articles processed: {category_stats[category]['articles_processed']}")
        logger.info(f"   📡 Feeds used: {category_stats[category]['feeds_used']}")
        
        all_markets.extend(final_category_markets)
        category_stats[category]["final_count"] = len(final_category_markets)
    
    # Create final output
    logger.info(f"\n🎉 PIPELINE COMPLETED!")
    logger.info("=" * 60)
    
    # Final deduplication across all categories
    final_markets = deduplicate_markets(all_markets)
    
    # Format output
    output = format_final_output(final_markets)
    
    # Save output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/full_pipeline_30_per_category_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Create summary
    summary = {
        "pipeline_run": {
            "timestamp": timestamp,
            "target_markets_per_category": 30,
            "target_categories": len(target_categories),
            "target_total_markets": len(target_categories) * 30,
            "actual_total_markets": len(final_markets),
            "success_rate": f"{(len(final_markets) / (len(target_categories) * 30)) * 100:.1f}%",
            "execution_time_minutes": f"{(time.time() - start_time) / 60:.1f}"
        },
        "category_breakdown": category_stats,
        "output_file": output_file
    }
    
    summary_file = f"outputs/pipeline_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print final summary
    logger.info(f"📊 FINAL RESULTS:")
    logger.info(f"   🎯 Target: {len(target_categories) * 30} markets")
    logger.info(f"   ✅ Generated: {len(final_markets)} markets")
    logger.info(f"   📈 Success Rate: {(len(final_markets) / (len(target_categories) * 30)) * 100:.1f}%")
    logger.info(f"   ⏱️  Execution Time: {(time.time() - start_time) / 60:.1f} minutes")
    logger.info(f"   📁 Output File: {output_file}")
    logger.info(f"   📋 Summary File: {summary_file}")
    
    print(f"\n🎉 PIPELINE COMPLETED!")
    print(f"📊 Generated {len(final_markets)} prediction markets")
    print(f"📁 Output: {output_file}")
    print(f"📋 Summary: {summary_file}")
    
    return output_file, summary_file

if __name__ == "__main__":
    run_comprehensive_pipeline()
