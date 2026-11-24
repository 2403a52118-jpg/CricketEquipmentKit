# 🏏 Cricket Kit & Equipment Management System

A production-ready web application for managing cricket equipment inventory, player registrations, kit issues, and returns. Built with **Python Flask**, **SQLite / PostgreSQL**, and pure **HTML5/CSS3/JavaScript**.

---

## 🚀 Features

- **📊 Real-time Dashboard**: Overview of kit categories, total stock, available inventory, currently borrowed items, and registered players.
- **⚡ Kit Issue & Stock Control**: Validation prevents issuing items when stock is insufficient.
- **🔄 Fast Returns**: One-click return processing automatically restores kit items back to active inventory.
- **👥 Player Management**: Player directory with phone numbers and history.
- **📦 Inventory Catalog**: Item tracking with status badges (*In Stock*, *Low Stock*, *Out of Stock*).
- **🗄️ Database Auto-Setup**: Automatic zero-config setup using local SQLite (`cricket_kit.db`) or enterprise PostgreSQL (via `DATABASE_URL` or `.env`).

---

## 🛠️ Project Structure

```
CricketKit/
├── app.py                 # Flask application backend
├── wsgi.py                # Production WSGI entry point (Waitress / Gunicorn)
├── cricket_kit.db         # SQLite database file (auto-generated)
├── database.sql           # Reference PostgreSQL schema & seed values
├── requirements.txt       # Cross-platform dependencies
├── Procfile               # Cloud deployment command (Render / Railway / Heroku)
├── render.yaml            # Render infrastructure-as-code deployment config
├── Dockerfile             # Container image configuration
├── vercel.json            # Vercel serverless configuration
├── start.bat              # Development runner & browser launcher (Windows)
├── deploy_local.bat       # Production WSGI server launcher (Windows)
├── .env.example           # PostgreSQL connection template
├── .gitignore             # Git ignore rules
├── static/
│   ├── style.css          # Responsive styling & status badges
│   └── script.js          # Client-side form validation & auto-dismiss alerts
└── templates/
    └── index.html         # Main dashboard view
```

---

## 💻 Running the Application

### Option A: 1-Click Launch (Windows)
- For Development server: Double-click **`start.bat`**
- For Production server: Double-click **`deploy_local.bat`**

### Option B: Terminal Command
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
# For Development:
python app.py

# For Production WSGI:
python wsgi.py
```
Then visit **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 🌐 Cloud Deployment Options

### 1. Render (Recommended - Free)
1. Push this repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com), click **New +** -> **Blueprint** or **Web Service**.
3. Select your repository. Render automatically reads `render.yaml` or uses:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`

### 2. Railway / Heroku / Fly.io
Deploy directly using the included `Procfile`:
```
web: gunicorn wsgi:app
```

### 3. Docker
```bash
docker build -t cricket-kit-app .
docker run -p 5000:5000 cricket-kit-app
```

---

## ⚙️ Environment Variables (Optional)

| Variable | Description | Default |
|---|---|---|
| `PORT` | Web server port | `5000` |
| `DATABASE_URL` | PostgreSQL connection URL | SQLite fallback |
| `SECRET_KEY` | Flask session key | Auto-generated |
