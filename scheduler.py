"""
Scheduler for the news pipeline.
Runs the pipeline at regular intervals.
"""
import time
import logging
import os
import datetime
import subprocess
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scheduler.log')
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline(output_dir: str = None):
    """
    Run the news pipeline.

    Args:
        output_dir: Directory to save the output file
    """
    try:
        # Create timestamp for the output file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Set up the output file path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"prediction_markets_{timestamp}.json")
        else:
            output_file = f"prediction_markets_{timestamp}.json"

        # Run the pipeline
        logger.info(f"Starting pipeline run at {timestamp}")
        cmd = ["python", "main.py", "--output", output_file]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logger.info(f"Pipeline run completed successfully. Output saved to {output_file}")
            logger.debug(f"Pipeline output: {stdout}")
            return True
        else:
            logger.error(f"Pipeline run failed with return code {process.returncode}")
            logger.error(f"Error: {stderr}")
            return False

    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}")
        return False

def run_scheduler(interval_minutes: int = 30, output_dir: str = None):
    """
    Run the scheduler to execute the pipeline at regular intervals.

    Args:
        interval_minutes: Interval between pipeline runs in minutes
        output_dir: Directory to save the output files
    """
    logger.info(f"Starting scheduler with {interval_minutes} minute interval")

    # Create the output directory if it doesn't exist
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

    try:
        # Run the pipeline immediately on startup
        logger.info("Running initial pipeline execution")
        run_pipeline(output_dir)

        while True:
            # Sleep until the next run
            logger.info(f"Waiting {interval_minutes} minutes until next run")
            time.sleep(interval_minutes * 60)

            # Run the pipeline
            success = run_pipeline(output_dir)

            if not success:
                logger.warning(f"Pipeline run failed. Will retry in {interval_minutes} minutes")

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
        # Continue running even if there's an error
        run_scheduler(interval_minutes, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduler for the news pipeline")
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval between pipeline runs in minutes"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Directory to save the output files"
    )

    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

    # Run the scheduler
    run_scheduler(args.interval, args.output_dir)
