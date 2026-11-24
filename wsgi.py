import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if os.name == "nt":
        from waitress import serve
        print(f"Starting Production WSGI server (Waitress) on http://localhost:{port} (0.0.0.0:{port})")
        serve(app, host="0.0.0.0", port=port)
    else:
        app.run(host="0.0.0.0", port=port)
