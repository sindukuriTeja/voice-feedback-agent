"""
Vercel Serverless Handler for FeedbackBot Pro
Serves the Streamlit app through Vercel's Python runtime.
"""
import sqlite3
import json
import os
from datetime import datetime

DB_NAME = "feedback_bot.db"

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        name TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        script TEXT,
        extra_instructions TEXT DEFAULT '',
        status TEXT DEFAULT 'Inactive',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        campaign_id INTEGER,
        q1 TEXT, q2 TEXT, q3 TEXT,
        notes TEXT,
        sentiment TEXT DEFAULT 'Neutral',
        score INTEGER DEFAULT 0,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level TEXT,
        message TEXT
    )''')
    conn.commit()
    conn.close()

def handler(request):
    """Vercel serverless function handler."""
    init_db()
    
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }
    
    if request.method == "OPTIONS":
        return ("", 204, headers)
    
    # API Routes
    if request.path == "/api/health":
        return (json.dumps({"status": "ok", "app": "FeedbackBot Pro"}), 200, headers)
    
    if request.path == "/api/stats":
        conn = sqlite3.connect(DB_NAME)
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM users WHERE status='Completed'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM users WHERE status='Pending'").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM campaigns WHERE status='Active'").fetchone()[0]
        avg_score = conn.execute("SELECT AVG(score) FROM results WHERE score > 0").fetchone()[0] or 0
        conn.close()
        return (json.dumps({
            "total_users": total_users,
            "completed": completed,
            "pending": pending,
            "active_campaigns": active,
            "avg_score": round(avg_score, 1)
        }), 200, headers)
    
    # Serve the main app HTML for all other routes
    if request.path == "/" or request.path.startswith("/app"):
        html = get_app_html()
        headers["Content-Type"] = "text/html"
        return (html, 200, headers)
    
    # Default: return API info
    return (json.dumps({
        "app": "FeedbackBot Pro",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/health - Health check",
            "GET /api/stats - Dashboard statistics",
            "GET / - Main application"
        ]
    }), 200, headers)

def get_app_html():
    """Return the main application HTML."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FeedbackBot Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; padding: 3rem 0; }
        .header h1 { font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }
        .header p { font-size: 1.2rem; color: #94a3b8; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .card { background: #1e293b; border-radius: 1rem; padding: 2rem; border: 1px solid #334155; }
        .card h3 { color: #60a5fa; margin-bottom: 1rem; }
        .card .value { font-size: 2.5rem; font-weight: bold; color: #f1f5f9; }
        .card .label { color: #94a3b8; margin-top: 0.5rem; }
        .footer { text-align: center; padding: 3rem 0; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎙️ FeedbackBot Pro</h1>
            <p>AI-Powered Voice Feedback Collection System</p>
        </div>
        <div class="grid" id="stats">
            <div class="card"><h3>Total Users</h3><div class="value" id="users">Loading...</div><div class="label">Registered users</div></div>
            <div class="card"><h3>Completed</h3><div class="value" id="completed">Loading...</div><div class="label">Interviews done</div></div>
            <div class="card"><h3>Pending</h3><div class="value" id="pending">Loading...</div><div class="label">Waiting for feedback</div></div>
            <div class="card"><h3>Avg Score</h3><div class="value" id="score">Loading...</div><div class="label">Out of 5.0</div></div>
        </div>
        <div class="footer">
            <p>Built with Streamlit, ElevenLabs, NVIDIA NIM & Faster-Whisper</p>
        </div>
    </div>
    <script>
        fetch('/api/stats')
            .then(r => r.json())
            .then(data => {
                document.getElementById('users').textContent = data.total_users;
                document.getElementById('completed').textContent = data.completed;
                document.getElementById('pending').textContent = data.pending;
                document.getElementById('score').textContent = data.avg_score + '/5';
            })
            .catch(() => {});
    </script>
</body>
</html>"""