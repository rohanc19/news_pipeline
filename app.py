"""
Simple web server for health checks on Render.
"""
import os
import threading
import time
from flask import Flask, jsonify, request
from scheduler import run_scheduler
import subprocess
import json

app = Flask(__name__)

# Global scheduler control
scheduler_thread = None
scheduler_running = False

# Start the scheduler in a background thread
def start_scheduler():
    global scheduler_running
    scheduler_running = True
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
        "scheduler": "running" if scheduler_running else "stopped",
        "output_files": file_count,
        "output_directory": output_dir
    })

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline_manually():
    """Manually trigger the pipeline to run once."""
    try:
        # Import and run the pipeline
        import sys
        import os
        sys.path.append(os.getcwd())

        print("🚀 Starting manual pipeline run...")

        # Run in a separate thread to avoid blocking
        def run_pipeline_thread():
            try:
                print("📦 Importing pipeline module...")
                from run_full_pipeline_30_per_category import run_comprehensive_pipeline

                print("🔄 Executing pipeline...")
                output_file, summary_file = run_comprehensive_pipeline()
                print(f"✅ Manual pipeline run completed: {output_file}")

            except ImportError as e:
                print(f"❌ Import error: {str(e)}")
                import traceback
                traceback.print_exc()

            except Exception as e:
                print(f"❌ Manual pipeline run failed: {str(e)}")
                import traceback
                traceback.print_exc()

        pipeline_thread = threading.Thread(target=run_pipeline_thread)
        pipeline_thread.daemon = True
        pipeline_thread.start()

        print("✅ Pipeline thread started")

        return jsonify({
            "status": "success",
            "message": "Pipeline started manually with enhanced logging",
            "note": "Check Render logs for detailed progress"
        })

    except Exception as e:
        print(f"❌ Failed to start pipeline: {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "status": "error",
            "message": f"Failed to start pipeline: {str(e)}"
        }), 500

@app.route('/scheduler/stop', methods=['POST'])
def stop_scheduler_endpoint():
    """Stop the automatic scheduler."""
    global scheduler_running
    scheduler_running = False

    return jsonify({
        "status": "success",
        "message": "Scheduler stopped",
        "scheduler": "stopped"
    })

@app.route('/scheduler/start', methods=['POST'])
def start_scheduler_endpoint():
    """Start the automatic scheduler."""
    global scheduler_thread, scheduler_running

    if not scheduler_running:
        scheduler_thread = threading.Thread(target=start_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()

        return jsonify({
            "status": "success",
            "message": "Scheduler started",
            "scheduler": "running"
        })
    else:
        return jsonify({
            "status": "info",
            "message": "Scheduler is already running",
            "scheduler": "running"
        })

@app.route('/scheduler/status')
def scheduler_status():
    """Get detailed scheduler status."""
    return jsonify({
        "scheduler_running": scheduler_running,
        "scheduler_thread_alive": scheduler_thread.is_alive() if scheduler_thread else False,
        "interval_minutes": int(os.environ.get("SCHEDULER_INTERVAL", "30")),
        "output_directory": os.environ.get("OUTPUT_DIR", "outputs")
    })

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
