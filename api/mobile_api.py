"""
XENO Mobile API Server
Flask REST API for mobile app communication
"""

import datetime
from functools import wraps
from typing import Any, Dict

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
app.config["SECRET_KEY"] = "your-secret-key-change-this"
app.config["JWT_EXPIRATION_HOURS"] = 24

import os

# Import XENO modules (adjust paths as needed)
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from modules.ai_chat_enhanced import ContextualAIChat
from modules.calendar_manager import CalendarManager
from modules.email_manager import EmailManager
from modules.github_integration import GitHubIntegration
from modules.linkedin_automation import LinkedInAutomation
from utils.timeline_manager import TimelineManager

# Initialize modules
email_manager = EmailManager()
github_integration = GitHubIntegration()
linkedin_automation = LinkedInAutomation()
calendar_manager = CalendarManager()
ai_chat = ContextualAIChat()
timeline_manager = TimelineManager()

# Store for push tokens
push_tokens = []


def token_required(f):
    """Decorator to require authentication token"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            if token.startswith("Bearer "):
                token = token[7:]
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token"""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Simple auth (replace with real authentication)
    if email and password:
        token = jwt.encode(
            {
                "email": email,
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(hours=app.config["JWT_EXPIRATION_HOURS"]),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        return jsonify({"token": token, "email": email})

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/dashboard", methods=["GET"])
@token_required
def get_dashboard():
    """Get dashboard overview"""
    try:
        # Get unread emails
        unread_emails = len(email_manager.get_unread_emails())

        # Get today's events
        today_events = len(calendar_manager.get_todays_events())

        # Get notifications count (placeholder)
        notifications = 0

        return jsonify(
            {
                "unread_emails": unread_emails,
                "upcoming_events": today_events,
                "notifications": notifications,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/timeline", methods=["GET"])
@token_required
def get_timeline():
    """Get recent activity timeline"""
    try:
        limit = request.args.get("limit", 20, type=int)
        activities = timeline_manager.get_recent_activities(limit)

        return jsonify(activities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notifications", methods=["GET"])
@token_required
def get_notifications():
    """Get notifications"""
    try:
        unread_only = request.args.get("unread_only", "false").lower() == "true"

        # Mock notifications (implement real notification system)
        notifications = [
            {
                "id": 1,
                "type": "email",
                "title": "New Email",
                "message": "You have new unread emails",
                "timestamp": datetime.datetime.now().isoformat(),
                "read": False,
            }
        ]

        if unread_only:
            notifications = [n for n in notifications if not n["read"]]

        return jsonify(notifications)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@token_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    # Implement notification marking logic
    return jsonify({"success": True})


@app.route("/api/push-token", methods=["POST"])
@token_required
def register_push_token():
    """Register device push notification token"""
    data = request.json
    token = data.get("token")

    if token and token not in push_tokens:
        push_tokens.append(token)

    return jsonify({"success": True})


@app.route("/api/emails", methods=["GET"])
@token_required
def get_emails():
    """Get emails from folder"""
    try:
        folder = request.args.get("folder", "INBOX")
        limit = request.args.get("limit", 50, type=int)

        emails = email_manager.get_emails(folder, limit)

        return jsonify(emails)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/emails/send", methods=["POST"])
@token_required
def send_email():
    """Send email"""
    try:
        data = request.json
        to = data.get("to")
        subject = data.get("subject")
        body = data.get("body")

        email_manager.send_email(to, subject, body)

        timeline_manager.add_activity("email_sent", "Email Sent", f"Sent email to {to}")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/calendar/events", methods=["GET"])
@token_required
def get_calendar_events():
    """Get calendar events"""
    try:
        days_ahead = request.args.get("days_ahead", 7, type=int)
        events = calendar_manager.get_upcoming_events(days_ahead=days_ahead)

        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/calendar/events", methods=["POST"])
@token_required
def create_calendar_event():
    """Create calendar event"""
    try:
        data = request.json

        event = calendar_manager.create_event(
            summary=data.get("summary"),
            start_time=datetime.datetime.fromisoformat(data.get("start_time")),
            end_time=datetime.datetime.fromisoformat(data.get("end_time")),
            description=data.get("description"),
            location=data.get("location"),
            attendees=data.get("attendees"),
        )

        timeline_manager.add_activity(
            "calendar_event", "Event Created", f"Created event: {data.get('summary')}"
        )

        return jsonify(event)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/voice/execute", methods=["POST"])
@token_required
def execute_voice_command():
    """Execute voice command"""
    try:
        data = request.json
        command = data.get("command")

        # Process voice command (implement command handler)
        result = f"Executed: {command}"

        timeline_manager.add_activity("voice_command", "Voice Command", command)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/repos", methods=["GET"])
@token_required
def get_github_repos():
    """Get GitHub repositories"""
    try:
        repos = github_integration.get_repositories()
        return jsonify(repos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/stats", methods=["GET"])
@token_required
def get_github_stats():
    """Get GitHub statistics"""
    try:
        stats = github_integration.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs", methods=["GET"])
@token_required
def get_jobs():
    """Search for jobs"""
    try:
        keywords = request.args.get("keywords", "")
        location = request.args.get("location", "")

        jobs = linkedin_automation.search_jobs(keywords, location)

        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>/apply", methods=["POST"])
@token_required
def apply_to_job(job_id):
    """Apply to a job"""
    try:
        # Get job details and apply
        result = linkedin_automation.apply_to_job(job_id)

        timeline_manager.add_activity(
            "job_application", "Job Application", f"Applied to job #{job_id}"
        )

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/chat", methods=["POST"])
@token_required
def ai_chat_message():
    """Send message to AI chat"""
    try:
        data = request.json
        message = data.get("message")
        context = data.get("context", [])

        response = ai_chat.chat(message, context)

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})


if __name__ == "__main__":
    print("🚀 XENO Mobile API Server Starting...")
    print("📱 Mobile apps can connect to: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
