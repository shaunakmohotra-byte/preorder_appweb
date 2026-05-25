from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix
import os

print("🔥 APP STARTING...")

# Create app
app = create_app()

# Check Mongo URI
MONGO_URI = os.environ.get("MONGO_URI")
print("MONGO_URI:", MONGO_URI)

if not MONGO_URI:
    raise Exception("❌ MONGO_URI not set")

# Fix proxy headers (for Render)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

# Local run (not used by Render, but good for testing)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
