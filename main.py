"""
Main entry point for the news pipeline.
"""
import argparse
import logging
import os
import json
from dotenv import load_dotenv

from pipeline import run_pipeline
from utils import setup_logging

# Load environment variables
load_dotenv()

def main():
    """
    Main entry point for the news pipeline.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="News Pipeline for Prediction Markets")
    parser.add_argument(
        "--output", 
        type=str, 
        default="prediction_markets.json",
        help="Output file path"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    parser.add_argument(
        "--category", 
        type=str, 
        help="Process only a specific category"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logging(log_level)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set")
        logger.info("Please set the GEMINI_API_KEY environment variable or create a .env file")
        return
    
    # Run the pipeline
    try:
        logger.info("Starting news pipeline")
        output = run_pipeline()
        
        # Save output to specified file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pipeline completed successfully. Output saved to {args.output}")
        
        # Print summary
        total_markets = len(output["eventsData"][0]["markets"])
        logger.info(f"Generated {total_markets} prediction markets")
        
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
