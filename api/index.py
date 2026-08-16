"""
Vercel Serverless Handler for FeedbackBot Pro
"""
import json
import os

DB_NAME = os.path.join(os.path.dirname(__file__), "..", "feedback_bot.db")

def init_db():
    conn = __import__("sqlite3").connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE,
        name TEXT, status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, script TEXT,
        extra_instructions TEXT DEFAULT '', status TEXT DEFAULT 'Inactive',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        campaign_id INTEGER, q1 TEXT, q2 TEXT, q3 TEXT, notes TEXT,
        sentiment TEXT DEFAULT 'Neutral', score INTEGER DEFAULT 0,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level TEXT, message TEXT)''')
    conn.commit()
    conn.close()

def handler(event, context):
    init_db()
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 204, "headers": headers, "body": ""}

    path = event.get("path", "/")

    if path == "/api/health":
        return {"statusCode": 200, "headers": {**headers, "Content-Type": "application/json"},
                "body": json.dumps({"status": "ok", "app": "FeedbackBot Pro"})}

    if path == "/api/stats":
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM users WHERE status='Completed'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM users WHERE status='Pending'").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM campaigns WHERE status='Active'").fetchone()[0]
        avg_row = conn.execute("SELECT AVG(score) FROM results WHERE score > 0").fetchone()[0]
        conn.close()
        return {"statusCode": 200, "headers": {**headers, "Content-Type": "application/json"},
                "body": json.dumps({"total_users": total_users, "completed": completed,
                    "pending": pending, "active_campaigns": active,
                    "avg_score": round(avg_row, 1) if avg_row else 0})}

    # Default: serve the landing page
    return {"statusCode": 200, "headers": {**headers, "Content-Type": "text/html"}, "body": LANDING_PAGE}

LANDING_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>FeedbackBot Pro</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f172a;color:#e2e8f0}
.container{max-width:1200px;margin:0 auto;padding:2rem}
.header{text-align:center;padding:3rem 0}
.header h1{font-size:3rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem}
.header p{font-size:1.2rem;color:#94a3b8}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.5rem;margin-top:2rem}
.card{background:#1e293b;border-radius:1rem;padding:2rem;border:1px solid #334155}
.card h3{color:#60a5fa;margin-bottom:1rem}
.card .value{font-size:2.5rem;font-weight:bold;color:#f1f5f9}
.card .label{color:#94a3b8;margin-top:.5rem}
.footer{text-align:center;padding:3rem 0;color:#64748b}
.btn{display:inline-block;margin-top:1rem;padding:.75rem 2rem;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-radius:.5rem;text-decoration:none;font-weight:600}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>&#127909; FeedbackBot Pro</h1>
<p>AI-Powered Voice Feedback Collection System</p>
<a class="btn" href="https://github.com/sindukuriTeja/voice-feedback-agent" target="_blank">View on GitHub</a>
</div>
<div class="grid" id="stats">
<div class="card"><h3>Total Users</h3><div class="value" id="users">...</div><div class="label">Registered users</div></div>
<div class="card"><h3>Completed</h3><div class="value" id="completed">...</div><div class="label">Interviews done</div></div>
<div class="card"><h3>Pending</h3><div class="value" id="pending">...</div><div class="label">Waiting for feedback</div></div>
<div class="card"><h3>Avg Score</h3><div class="value" id="score">...</div><div class="label">Out of 5.0</div></div>
</div>
<div class="footer"><p>Built with Streamlit, ElevenLabs, NVIDIA NIM &amp; Faster-Whisper</p></div>
</div>
<script>
fetch('/api/stats').then(r=>r.json()).then(d=>{
document.getElementById('users').textContent=d.total_users;
document.getElementById('completed').textContent=d.completed;
document.getElementById('pending').textContent=d.pending;
document.getElementById('score').textContent=d.avg_score+'/5';
}).catch(()=>{});
</script>
</body>
</html>"""