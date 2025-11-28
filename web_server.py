"""
Flask backend server for XENO Job Hunter web interface
"""
import logging
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from jobs.job_hunter import JobHunter

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web.server")
job_hunter = None


@app.route("/")
def index():
    """Serve the main page"""
    return send_from_directory(str(project_root / "web" / "jobs"), "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files"""
    return send_from_directory(str(project_root / "web" / "jobs"), path)


@app.route("/search-jobs", methods=["POST"])
def search_jobs():
    """Search for jobs based on criteria"""
    global job_hunter

    try:
        # Initialize job hunter if not already done
        if job_hunter is None:
            job_hunter = JobHunter()
            logger.info("JobHunter initialized")

        # Get request data
        data = request.get_json()
        keywords = data.get("keywords", [])
        location = data.get("location", "France")
        job_types = data.get("job_type", ["internship"])
        sources = data.get("sources", ["welcometothejungle", "remotive", "wellfound"])
        max_per_source = data.get("max_per_source", 25)

        logger.info(f"Searching jobs: keywords={keywords}, location={location}, sources={sources}")

        # Search jobs
        jobs = job_hunter.search_jobs(
            keywords=keywords,
            location=location,
            job_types=job_types,
            sources=sources,
            max_per_source=max_per_source,
        )

        logger.info(f"Found {len(jobs)} jobs")

        return jsonify({"success": True, "jobs": jobs, "count": len(jobs)})

    except Exception as e:
        logger.error(f"Error searching jobs: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e), "jobs": []}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "XENO Job Hunter API"})


if __name__ == "__main__":
    logger.info("Starting XENO Job Hunter web server...")
    logger.info("Access the interface at: http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
