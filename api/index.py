from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "FeedbackBot Pro"})


@app.route("/api/stats")
def stats():
    return jsonify({"total_users": 0, "completed": 0, "pending": 0, "active_campaigns": 0, "avg_score": 0})


@app.route("/")
def index():
    return """<!DOCTYPE html>
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
h1{font-size:3rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem}
p{font-size:1.2rem;color:#94a3b8}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.5rem;margin-top:2rem}
.card{background:#1e293b;border-radius:1rem;padding:2rem;border:1px solid #334155}
h3{color:#60a5fa;margin-bottom:1rem}
.value{font-size:2.5rem;font-weight:bold;color:#f1f5f9}
.label{color:#94a3b8;margin-top:.5rem}
.footer{text-align:center;padding:3rem 0;color:#64748b}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>&#127909; FeedbackBot Pro</h1>
<p>AI-Powered Voice Feedback Collection System</p>
</div>
<div class="grid">
<div class="card"><h3>Total Users</h3><div class="value" id="users">0</div><div class="label">Registered users</div></div>
<div class="card"><h3>Completed</h3><div class="value" id="completed">0</div><div class="label">Interviews done</div></div>
<div class="card"><h3>Pending</h3><div class="value" id="pending">0</div><div class="label">Waiting for feedback</div></div>
<div class="card"><h3>Avg Score</h3><div class="value" id="score">0/5</div><div class="label">Out of 5.0</div></div>
</div>
<div class="footer"><p>Built with Streamlit, ElevenLabs, NVIDIA NIM &amp; Faster-Whisper</p></div>
</div>
</body>
</html>"""