"""
FeedbackBot Pro - Professional AI Voice Feedback Dashboard
A complete SaaS-style web application for managing AI voice feedback campaigns.
"""
import streamlit as st
import sqlite3
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

DB_NAME = "feedback_bot.db"

# --- Page Configuration ---
st.set_page_config(
    page_title="FeedbackBot Pro",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    .main-header { 
        font-size: 2.5rem; 
        font-weight: bold; 
        color: #1f77b4; 
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-top: 20px;
    }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; 
        border-radius: 15px; 
        margin: 10px 0;
        color: white;
    }
    .success-box { 
        background-color: #d4edda; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #28a745; 
        margin: 10px 0;
    }
    .warning-box { 
        background-color: #fff3cd; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #ffc107; 
        margin: 10px 0;
    }
    .error-box { 
        background-color: #f8d7da; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #dc3545; 
        margin: 10px 0;
    }
    .info-box { 
        background-color: #d1ecf1; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #17a2b8; 
        margin: 10px 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Database Functions ---
def init_db():
    """Initialize the SQLite database with all required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        name TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Campaigns Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        script TEXT,
        extra_instructions TEXT DEFAULT '',
        status TEXT DEFAULT 'Inactive',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Results Table
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
    
    # Logs Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level TEXT,
        message TEXT
    )''')
    
    conn.commit()
    conn.close()

def add_log(level, message):
    """Add a log entry to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO logs (level, message) VALUES (?, ?)", (level, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Log Error: {e}")

# --- Sidebar Navigation ---
st.sidebar.markdown("## 🎙️ FeedbackBot Pro")
st.sidebar.markdown("AI-Powered Voice Feedback Platform")
st.sidebar.markdown("---")

pages = {
    "🏠 Dashboard": "dashboard",
    "👥 Users": "users",
    "📝 Campaigns": "campaigns",
    "📊 Results": "results",
    "📈 Analytics": "analytics",
    "🔧 Live Monitor": "monitor",
    "⚙️ Settings": "settings",
    "🛠️ Developer Hub": "developer"
}

selected_page = st.sidebar.radio("Navigate", list(pages.keys()), index=0)
page = pages[selected_page]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")

conn = sqlite3.connect(DB_NAME)
total_users = pd.read_sql_query("SELECT COUNT(*) as Total FROM users", conn)["Total"][0]
completed = pd.read_sql_query("SELECT COUNT(*) as Completed FROM users WHERE status='Completed'", conn)["Completed"][0]
pending = pd.read_sql_query("SELECT COUNT(*) as Pending FROM users WHERE status='Pending'", conn)["Pending"][0]
active_campaigns = pd.read_sql_query("SELECT COUNT(*) as Active FROM campaigns WHERE status='Active'", conn)["Active"][0]
conn.close()

col1, col2 = st.sidebar.columns(2)
col1.metric("Total Users", total_users)
col2.metric("Completed", completed)
col3, col4 = st.sidebar.columns(2)
col3.metric("Pending", pending)
col4.metric("Active", active_campaigns)

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("FeedbackBot Pro v1.0\nAI Voice Feedback Collection System")

# --- Initialize Database ---
init_db()

# =====================================================================
# PAGE 1: DASHBOARD
# =====================================================================
if page == "dashboard":
    st.markdown("<h1 class='main-header'>🏠 Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("Welcome to **FeedbackBot Pro** - Your AI-powered voice feedback platform.")
    st.markdown("---")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Users</h3>
            <h1>{}</h1>
        </div>
        """.format(total_users), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Completed</h3>
            <h1>{}</h1>
        </div>
        """.format(completed), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Pending</h3>
            <h1>{}</h1>
        </div>
        """.format(pending), unsafe_allow_html=True)
    
    with col4:
        avg_score = 0
        conn = sqlite3.connect(DB_NAME)
        score_data = pd.read_sql_query("SELECT AVG(score) as Avg FROM results WHERE score > 0", conn)
        if score_data["Avg"][0]:
            avg_score = score_data["Avg"][0]
        conn.close()
        st.markdown("""
        <div class="metric-card">
            <h3>Avg Score</h3>
            <h1>{:.1f}/5</h1>
        </div>
        """.format(avg_score), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Two Column Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h2 class='sub-header'>📋 Recent Activity</h2>", unsafe_allow_html=True)
        conn = sqlite3.connect(DB_NAME)
        recent_results = pd.read_sql_query("""
            SELECT r.*, u.name, u.phone, c.name as campaign 
            FROM results r 
            JOIN users u ON r.user_id = u.id 
            JOIN campaigns c ON r.campaign_id = c.id 
            ORDER BY r.completed_at DESC LIMIT 5
        """, conn)
        conn.close()
        
        if not recent_results.empty:
            st.dataframe(recent_results[["name", "phone", "campaign", "score", "sentiment"]], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("No results yet. Start a campaign to see results here!")
    
    with col2:
        st.markdown("<h2 class='sub-header'>⚡ Quick Actions</h2>", unsafe_allow_html=True)
        
        if st.button("➕ Add New User", type="primary", use_container_width=True):
            st.session_state["go_to"] = "users"
            st.rerun()
        
        if st.button("📝 Create Campaign", type="primary", use_container_width=True):
            st.session_state["go_to"] = "campaigns"
            st.rerun()
        
        if st.button("📊 View Results", type="primary", use_container_width=True):
            st.session_state["go_to"] = "results"
            st.rerun()
        
        if st.button("📈 View Analytics", type="primary", use_container_width=True):
            st.session_state["go_to"] = "analytics"
            st.rerun()
    
    # Handle navigation from quick actions
    if "go_to" in st.session_state:
        st.session_state.pop("go_to")

# =====================================================================
# PAGE 2: USERS
# =====================================================================
elif page == "users":
    st.markdown("<h1 class='main-header'>👥 User Management</h1>", unsafe_allow_html=True)
    
    # Add User Form
    with st.expander("➕ Add New User", expanded=True):
        with st.form("add_user"):
            col1, col2, col3 = st.columns(3)
            with col1: 
                phone = st.text_input("Phone Number", placeholder="+919876543210")
            with col2: 
                name = st.text_input("Name", placeholder="John Doe")
            with col3: 
                status = st.selectbox("Status", ["Pending", "Completed", "Skipped"])
            
            if st.form_submit_button("✅ Add User", type="primary"):
                if phone:
                    conn = sqlite3.connect(DB_NAME)
                    try:
                        conn.execute("INSERT INTO users (phone, name, status) VALUES (?, ?, ?)", 
                                   (phone, name, status))
                        conn.commit()
                        st.success(f"✅ Added {name or phone}!")
                        add_log("INFO", f"User added: {name or phone}")
                    except sqlite3.IntegrityError:
                        st.error("❌ Phone number already exists.")
                    conn.close()
                    st.rerun()
                else:
                    st.error("❌ Phone number is required!")
    
    # Bulk Upload
    with st.expander("📁 Bulk Upload Users (CSV)"):
        st.markdown("Upload a CSV file with columns: `phone`, `name`")
        uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                if "phone" in df.columns:
                    conn = sqlite3.connect(DB_NAME)
                    count = 0
                    for _, row in df.iterrows():
                        try:
                            conn.execute("INSERT INTO users (phone, name) VALUES (?, ?)", 
                                       (str(row["phone"]), str(row.get("name", ""))))
                            count += 1
                        except:
                            pass
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Added {count} users!")
                    add_log("INFO", f"Bulk upload: {count} users added")
                    st.rerun()
                else:
                    st.error("❌ CSV must have a 'phone' column!")
            except Exception as e:
                st.error(f"❌ Error reading CSV: {e}")
    
    # User List with Filters
    st.markdown("---")
    st.markdown("<h2 class='sub-header'>📋 All Users</h2>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM users ORDER BY created_at DESC", conn)
    conn.close()
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Filter by Status", 
                                          ["Pending", "Completed", "Skipped"], 
                                          default=["Pending", "Completed", "Skipped"])
        with col2:
            search = st.text_input("🔍 Search by Name or Phone")
        
        filtered = df[df["status"].isin(status_filter)]
        if search:
            filtered = filtered[
                filtered["name"].str.contains(search, case=False, na=False) | 
                filtered["phone"].str.contains(search, case=False, na=False)
            ]
        
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        
        # Delete User
        with st.expander("🗑️ Delete Users"):
            selected_user = st.selectbox("Select user to delete", filtered["name"].tolist())
            if st.button("🗑️ Delete Selected User", type="primary"):
                conn = sqlite3.connect(DB_NAME)
                conn.execute("DELETE FROM users WHERE name=?", (selected_user,))
                conn.commit()
                conn.close()
                st.success(f"✅ Deleted {selected_user}")
                add_log("INFO", f"User deleted: {selected_user}")
                st.rerun()
    else:
        st.info("No users added yet. Add users above!")

# =====================================================================
# PAGE 3: CAMPAIGNS
# =====================================================================
elif page == "campaigns":
    st.markdown("<h1 class='main-header'>📝 Campaign Manager</h1>", unsafe_allow_html=True)
    
    # Create Campaign
    with st.expander("➕ Create New Campaign", expanded=True):
        with st.form("new_campaign"):
            col1, col2 = st.columns(2)
            with col1:
                camp_name = st.text_input("Campaign Name", placeholder="Product Feedback Q4")
            with col2:
                camp_status = st.selectbox("Initial Status", ["Inactive", "Active"])
            
            script = st.text_area(
                "📋 AI Script", 
                placeholder="Ask the user 3 questions:\n1. How satisfied are you with our product?\n2. Is the price fair?\n3. Would you recommend us to others?",
                height=150
            )
            
            extra_instructions = st.text_area(
                "🎯 Extra AI Instructions (Optional)",
                placeholder="Be polite, speak in English, keep responses short.",
                height=75
            )
            
            if st.form_submit_button("✅ Create Campaign", type="primary"):
                if camp_name and script:
                    conn = sqlite3.connect(DB_NAME)
                    conn.execute(
                        "INSERT INTO campaigns (name, script, extra_instructions, status) VALUES (?, ?, ?, ?)", 
                        (camp_name, script, extra_instructions, camp_status)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Campaign created!")
                    add_log("INFO", f"Campaign created: {camp_name}")
                    st.rerun()
                else:
                    st.error("❌ Campaign name and script are required!")
    
    # List Campaigns
    st.markdown("---")
    st.markdown("<h2 class='sub-header'>📋 Your Campaigns</h2>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM campaigns ORDER BY created_at DESC", conn)
    conn.close()
    
    if not df.empty:
        for _, row in df.iterrows():
            status_emoji = {"Inactive": "⏸️", "Active": "▶️", "Paused": "⏹️", "Completed": "✅"}.get(row['status'], "❓")
            
            with st.expander(f"**{status_emoji} {row['name']}** (Status: {row['status']})"):
                st.markdown(f"**Script:** {row['script']}")
                if row['extra_instructions']:
                    st.markdown(f"**Extra Instructions:** {row['extra_instructions']}")
                st.caption(f"Created: {row['created_at']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if row['status'] in ['Inactive', 'Paused'] and st.button(f"▶️ Start", key=f"start_{row['id']}", type="primary"):
                        conn = sqlite3.connect(DB_NAME)
                        conn.execute("UPDATE campaigns SET status='Active', updated_at=CURRENT_TIMESTAMP WHERE id=?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.success("✅ Campaign started!")
                        add_log("INFO", f"Campaign started: {row['name']}")
                        st.rerun()
                with col2:
                    if row['status'] == 'Active' and st.button(f"⏹️ Pause", key=f"pause_{row['id']}"):
                        conn = sqlite3.connect(DB_NAME)
                        conn.execute("UPDATE campaigns SET status='Paused', updated_at=CURRENT_TIMESTAMP WHERE id=?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.warning("⏸️ Campaign paused!")
                        add_log("INFO", f"Campaign paused: {row['name']}")
                        st.rerun()
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{row['id']}"):
                        conn = sqlite3.connect(DB_NAME)
                        conn.execute("DELETE FROM campaigns WHERE id=?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.success("🗑️ Campaign deleted!")
                        add_log("INFO", f"Campaign deleted: {row['name']}")
                        st.rerun()
    else:
        st.info("No campaigns created yet. Create one above!")

# =====================================================================
# PAGE 4: RESULTS
# =====================================================================
elif page == "results":
    st.markdown("<h1 class='main-header'>📊 Feedback Results</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("""
        SELECT r.*, u.name, u.phone, c.name as campaign 
        FROM results r 
        JOIN users u ON r.user_id = u.id
        JOIN campaigns c ON r.campaign_id = c.id
        ORDER BY r.completed_at DESC
    """, conn)
    conn.close()
    
    if not df.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            campaign_filter = st.multiselect("Filter by Campaign", 
                                           df["campaign"].unique().tolist(), 
                                           default=df["campaign"].unique().tolist())
        with col2:
            sentiment_filter = st.multiselect("Filter by Sentiment", 
                                            ["Positive", "Neutral", "Negative"], 
                                            default=["Positive", "Neutral", "Negative"])
        with col3:
            score_filter = st.slider("Score Range", 0, 5, (0, 5))
        
        filtered = df[
            (df["campaign"].isin(campaign_filter)) & 
            (df["sentiment"].isin(sentiment_filter)) &
            (df["score"] >= score_filter[0]) & 
            (df["score"] <= score_filter[1])
        ]
        
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        
        # Export
        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "results.csv", "text/csv")
        
        # Summary
        st.markdown("---")
        st.markdown("<h2 class='sub-header'>📈 Summary</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Responses", len(filtered))
        col2.metric("Avg Score", f"{filtered['score'].mean():.1f}/5" if len(filtered) else "N/A")
        col3.metric("Positive Sentiment", f"{len(filtered[filtered['sentiment']=='Positive'])}/{len(filtered)}")
    else:
        st.info("No results yet. Start a campaign and complete interviews to see results here!")

# =====================================================================
# PAGE 5: ANALYTICS
# =====================================================================
elif page == "analytics":
    st.markdown("<h1 class='main-header'>📈 Analytics</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("""
        SELECT r.*, u.name, u.phone, c.name as campaign 
        FROM results r 
        JOIN users u ON r.user_id = u.id
        JOIN campaigns c ON r.campaign_id = c.id
    """, conn)
    conn.close()
    
    if not df.empty:
        # Score Distribution
        st.markdown("<h2 class='sub-header'>📊 Score Distribution</h2>", unsafe_allow_html=True)
        fig = px.histogram(df, x="score", nbins=5, title="Feedback Score Distribution",
                          color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment Pie Chart
        st.markdown("<h2 class='sub-header'>🎭 Sentiment Analysis</h2>", unsafe_allow_html=True)
        fig = px.pie(df, values="id", names="sentiment", title="Sentiment Distribution",
                    color_discrete_sequence=['#00CC96', '#FFA15A', '#FF6B6B'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Campaign Performance
        st.markdown("<h2 class='sub-header'>🏆 Campaign Performance</h2>", unsafe_allow_html=True)
        campaign_stats = df.groupby("campaign").agg({
            "score": "mean",
            "id": "count"
        }).reset_index()
        campaign_stats.columns = ["Campaign", "Avg Score", "Responses"]
        
        fig = px.bar(campaign_stats, x="Campaign", y="Avg Score", title="Average Score by Campaign",
                    color="Avg Score", color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
        
        # Timeline
        st.markdown("<h2 class='sub-header'>📅 Response Timeline</h2>", unsafe_allow_html=True)
        df_copy = df.copy()
        df_copy["completed_at"] = pd.to_datetime(df_copy["completed_at"])
        fig = px.line(df_copy, x="completed_at", y="score", title="Score Over Time",
                     color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for analytics yet. Complete some interviews first!")

# =====================================================================
# PAGE 6: LIVE MONITOR
# =====================================================================
elif page == "monitor":
    st.markdown("<h1 class='main-header'>🔧 Live Monitor</h1>", unsafe_allow_html=True)
    st.markdown("Watch the AI agent work in real-time. Logs are updated as the worker processes interviews.")
    
    # Live Log Viewer
    st.markdown("<h2 class='sub-header'>📝 Live Logs</h2>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_NAME)
    logs = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100", conn)
    conn.close()
    
    if not logs.empty:
        for _, log in logs.iterrows():
            if log["level"] == "INFO":
                st.info(f"🕐 {log['timestamp']} - {log['message']}")
            elif log["level"] == "WARNING":
                st.warning(f"🕐 {log['timestamp']} - {log['message']}")
            elif log["level"] == "ERROR":
                st.error(f"🕐 {log['timestamp']} - {log['message']}")
            else:
                st.text(f"🕐 {log['timestamp']} - {log['message']}")
    else:
        st.info("No logs yet. Start the worker to see live logs here!")
    
    # Auto-refresh
    st.markdown("---")
    if st.checkbox("🔄 Auto-refresh logs (every 5 seconds)"):
        time.sleep(5)
        st.rerun()

# =====================================================================
# PAGE 7: SETTINGS
# =====================================================================
elif page == "settings":
    st.markdown("<h1 class='main-header'>⚙️ Settings</h1>", unsafe_allow_html=True)
    
    # API Keys
    st.markdown("<h2 class='sub-header'>🔑 API Keys</h2>", unsafe_allow_html=True)
    
    with st.expander("ElevenLabs API Key"):
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
        if elevenlabs_key:
            st.success(f"✅ Configured: {elevenlabs_key[:10]}...")
        else:
            st.warning("⚠️ Not configured")
        st.info("Your ElevenLabs API key is configured in the `.env` file.")
    
    with st.expander("NVIDIA API Key"):
        nvidia_key = os.getenv("NVIDIA_API_KEY", "")
        if nvidia_key:
            st.success(f"✅ Configured: {nvidia_key[:10]}...")
        else:
            st.warning("⚠️ Not configured")
        st.info("Your NVIDIA API key is configured in the `.env` file.")
    
    # Voice Settings
    st.markdown("<h2 class='sub-header'>🎤 Voice Settings</h2>", unsafe_allow_html=True)
    st.selectbox("Voice", ["Rachel (Female)", "Domi (Female)", "Bella (Female)", "Antoni (Male)", "Thomas (Male)"])
    st.slider("Speech Speed", 0.5, 2.0, 1.0)
    
    # AI Settings
    st.markdown("<h2 class='sub-header'>🧠 AI Settings</h2>", unsafe_allow_html=True)
    st.selectbox("AI Model", ["NVIDIA NIM (Llama 3.1 8B)", "Ollama (Qwen3 4B - Local)"])
    st.slider("AI Temperature", 0.0, 1.0, 0.7)
    
    st.markdown("---")
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved!")

# =====================================================================
# PAGE 8: DEVELOPER HUB
# =====================================================================
elif page == "developer":
    st.markdown("<h1 class='main-header'>🛠️ Developer Hub</h1>", unsafe_allow_html=True)
    st.markdown("Extend and customize your FeedbackBot Pro application.")
    
    # API Documentation
    with st.expander("📚 Database Schema", expanded=True):
        st.markdown("""
        ### Users Table
        - `id` (INTEGER, PRIMARY KEY)
        - `phone` (TEXT, UNIQUE)
        - `name` (TEXT)
        - `status` (TEXT: Pending/Completed/Skipped)
        - `created_at` (TIMESTAMP)
        
        ### Campaigns Table
        - `id` (INTEGER, PRIMARY KEY)
        - `name` (TEXT)
        - `script` (TEXT)
        - `extra_instructions` (TEXT)
        - `status` (TEXT: Inactive/Active/Paused/Completed)
        - `created_at` (TIMESTAMP)
        
        ### Results Table
        - `id` (INTEGER, PRIMARY KEY)
        - `user_id` (INTEGER, FOREIGN KEY)
        - `campaign_id` (INTEGER, FOREIGN KEY)
        - `q1, q2, q3` (TEXT)
        - `notes` (TEXT)
        - `sentiment` (TEXT: Positive/Neutral/Negative)
        - `score` (INTEGER: 0-5)
        - `completed_at` (TIMESTAMP)
        
        ### Logs Table
        - `id` (INTEGER, PRIMARY KEY)
        - `timestamp` (TIMESTAMP)
        - `level` (TEXT: INFO/WARNING/ERROR)
        - `message` (TEXT)
        """)
    
    # System Info
    st.markdown("<h2 class='sub-header'>ℹ️ System Information</h2>", unsafe_allow_html=True)
    st.json({
        "version": "1.0.0",
        "name": "FeedbackBot Pro",
        "database": "SQLite",
        "ai_model": "NVIDIA NIM (Llama 3.1 8B)",
        "tts_provider": "ElevenLabs",
        "stt_provider": "Faster-Whisper",
        "framework": "Streamlit",
        "features": [
            "AI Voice Interviews",
            "Sentiment Analysis",
            "Score Tracking (0-5)",
            "Real-time Monitoring",
            "CSV Export",
            "Analytics Dashboard",
            "Bulk User Upload",
            "Campaign Management"
        ]
    })
    
    # Quick Commands
    st.markdown("<h2 class='sub-header'>🚀 Quick Commands</h2>", unsafe_allow_html=True)
    st.code("""
# Install dependencies
pip install -r requirements.txt

# Start the website
streamlit run app.py

# Start the AI worker
python worker.py
""", language="bash")