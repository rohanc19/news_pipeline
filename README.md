# News Pipeline for Prediction Markets

An intelligent AI pipeline that processes RSS feeds into prediction market questions with Kalshi-style formatting.

## Overview

This pipeline:

1. Fetches articles from predefined RSS feeds across multiple categories
2. Processes and extracts content from the past 5 days
3. Uses Gemini 1.5 Flash (or equivalent LLM) to generate:
   - Yes/No prediction questions
   - Verifiable timeframes
   - Prediction-oriented explanations
   - Relevant tags
4. Formats the output into a structured JSON format

## Features

- Processes multiple categories: Politics, Crypto, Companies, Economics, Sports, Culture, Climate, Tech & Science, Financials, Health, World, Trending, New
- Generates exactly 30 unique prediction markets per category
- Implements fallback logic for insufficient articles
- Deduplicates markets across categories
- Checkpoints progress to allow for resuming interrupted runs

## Requirements

- Python 3.8+
- Google Gemini API key

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Running the Pipeline Once

Run the pipeline with default settings:

```bash
python main.py
```

#### Command-line Options

- `--output`: Specify the output file path (default: `prediction_markets.json`)
- `--log-level`: Set the logging level (default: `INFO`)
- `--category`: Process only a specific category

Example:

```bash
python main.py --output markets_2023_05_10.json --log-level DEBUG --category Crypto
```

### Running the Pipeline on a Schedule

The pipeline can be scheduled to run automatically at regular intervals using the scheduler:

```bash
python scheduler.py --interval 30 --output-dir outputs
```

#### Command-line Options

- `--interval`: Interval between pipeline runs in minutes (default: 30)
- `--output-dir`: Directory to save the output files (default: "outputs")

### Using the Batch Scripts

For Windows users, batch scripts are provided to easily start and stop the scheduler:

1. Start the scheduler in the background:
   ```
   run_scheduler.bat
   ```

2. Stop the scheduler:
   ```
   stop_scheduler.bat
   ```

The scheduler will run the pipeline every 30 minutes and save the output files to the "outputs" directory. Logs are saved to `scheduler.log` and `scheduler_output.log`.

## Output Format

The pipeline generates a JSON file with the following structure:

```json
{
  "eventsData": [
    {
      "markets": [
        {
          "id": "market_xxxxxxxx",
          "title": "Will India pass the crypto bill by December 31, 2025?",
          "description": "[Kalshi-style prediction explanation]",
          "category": "Crypto",
          "tags": ["Crypto", "Currency", "Government"],
          "status": "open",
          "createdAt": "2025-05-08T04:00:00Z",
          "startTime": "2025-05-08T04:00:00Z",
          "endTime": "2025-12-31T23:59:59Z",
          "resolutionTime": "2026-01-01T12:00:00Z",
          "result": null,
          "yesCount": 50000,
          "noCount": 50000,
          "totalVolume": 100000,
          "currentYesProbability": 0.5,
          "currentNoProbability": 0.5,
          "creatorId": "kalshi-generator",
          "resolutionSource": "[Original article URL]"
        }
      ]
    }
  ]
}
```

## Project Structure

- `main.py`: Entry point script
- `pipeline.py`: Main pipeline orchestration
- `config.py`: Configuration settings
- `feed_parser.py`: RSS feed parsing
- `article_processor.py`: Article content processing
- `llm_service.py`: LLM integration
- `output_formatter.py`: JSON output formatting
- `utils.py`: Utility functions
- `scheduler.py`: Scheduler for running the pipeline at regular intervals
- `run_scheduler.bat`: Batch script to start the scheduler in the background
- `stop_scheduler.bat`: Batch script to stop the scheduler

## Customization

You can customize the pipeline by modifying the following files:

- `config.py`: Add or modify RSS feeds, change LLM settings, adjust pipeline parameters
- `llm_service.py`: Modify prompts to change the style of generated prediction markets
- `strapi_service.py`: Adjust the Strapi integration to match your content types

## Strapi Integration

The pipeline can send generated prediction markets to a Strapi CMS instance:

1. Set up a Strapi instance with a "prediction-markets" content type
2. Create an API token in Strapi with appropriate permissions
3. Add the following environment variables:
   - `STRAPI_API_URL`: URL of your Strapi instance (e.g., https://your-strapi-instance.com)
   - `STRAPI_API_TOKEN`: Your Strapi API token

When the pipeline runs, it will:
1. Generate prediction markets as usual
2. Save them to a local JSON file
3. Send each market to your Strapi instance via the API

## Deployment to Render

This project can be easily deployed to Render using the provided configuration files.

### Prerequisites

1. Create a [Render](https://render.com/) account if you don't have one
2. Have your Google Gemini API key ready

### Deployment Steps

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. In the Render dashboard, click "New" and select "Blueprint"
3. Connect your Git repository
4. Render will automatically detect the `render.yaml` configuration
5. Add your `GEMINI_API_KEY` as an environment variable in the Render dashboard
6. Click "Apply" to deploy the service

The news pipeline will automatically run every 30 minutes and save the output to the `outputs` directory.

### Manual Deployment

If you prefer to deploy manually:

1. In the Render dashboard, click "New" and select "Web Service"
2. Connect your Git repository
3. Configure the service:
   - Name: `news-pipeline` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python scheduler.py --interval 30 --output-dir outputs`
4. Add your `GEMINI_API_KEY` as an environment variable
5. Click "Create Web Service" to deploy

## License

MIT
