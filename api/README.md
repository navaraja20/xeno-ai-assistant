# XENO Mobile API Server

Flask-based REST API server for XENO mobile app communication.

## Setup

1. Install dependencies:
```bash
pip install flask flask-cors pyjwt
```

2. Start the server:
```bash
python api/mobile_api.py
```

Server will run on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token

### Dashboard
- `GET /api/dashboard` - Get dashboard overview
- `GET /api/timeline` - Get recent activity timeline

### Notifications
- `GET /api/notifications` - Get notifications
- `POST /api/notifications/:id/read` - Mark notification as read
- `POST /api/push-token` - Register push notification token

### Email
- `GET /api/emails` - Get emails
- `POST /api/emails/send` - Send email

### Calendar
- `GET /api/calendar/events` - Get calendar events
- `POST /api/calendar/events` - Create calendar event

### Voice Commands
- `POST /api/voice/execute` - Execute voice command

### GitHub
- `GET /api/github/repos` - Get GitHub repositories
- `GET /api/github/stats` - Get GitHub statistics

### Jobs
- `GET /api/jobs` - Search for jobs
- `POST /api/jobs/:id/apply` - Apply to a job

### AI Chat
- `POST /api/ai/chat` - Send message to AI chat

### Health
- `GET /api/health` - Health check

## Authentication

All endpoints except `/api/auth/login` and `/api/health` require JWT authentication.

Include the token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Mobile App Configuration

Update the server URL in the mobile app:
1. Open `mobile/src/services/XenoAPI.js`
2. Change `API_BASE_URL` to your server's IP address
3. Example: `http://192.168.1.100:5000/api`

## Security Notes

⚠️ **Important**: Change the `SECRET_KEY` in `mobile_api.py` before deploying to production!

The current authentication is simplified for development. Implement proper user authentication for production use.
