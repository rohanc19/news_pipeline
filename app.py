"""
Simple web server for health checks on Render.
"""
import os
import threading
import time
from flask import Flask, jsonify
from scheduler import run_scheduler

app = Flask(__name__)

# Start the scheduler in a background thread
def start_scheduler():
    interval = int(os.environ.get("SCHEDULER_INTERVAL", "30"))
    output_dir = os.environ.get("OUTPUT_DIR", "outputs")
    run_scheduler(interval, output_dir)

# Start the scheduler thread when the app starts
scheduler_thread = threading.Thread(target=start_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "news-pipeline",
        "scheduler": "running"
    })

@app.route('/status')
def status():
    """Status endpoint with more details."""
    # Check if outputs directory exists and get file count
    output_dir = os.environ.get("OUTPUT_DIR", "outputs")
    file_count = 0
    if os.path.exists(output_dir):
        file_count = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
    
    return jsonify({
        "status": "healthy",
        "service": "news-pipeline",
        "scheduler": "running",
        "output_files": file_count,
        "output_directory": output_dir
    })

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
