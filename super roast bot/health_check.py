"""
Health Check Endpoint for Super RoastBot
Provides a simple GET /health endpoint for monitoring and deployment checks.
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint that returns application status.
    Returns:
        JSON response with status and message
    """
    health_status = {
        "status": "healthy",
        "service": "Super RoastBot",
        "message": "Service is running and available"
    }
    return jsonify(health_status), 200

if __name__ == '__main__':
    # Run on port 5000 (separate from Streamlit's default 8501)
    port = int(os.environ.get('HEALTH_CHECK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
