from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    print("🔥 APP STARTING...")

    ...
    
    MONGO_URI = os.environ.get("MONGO_URI")
    print("MONGO_URI:", MONGO_URI)

    if not MONGO_URI:
        raise Exception("MONGO_URI not set")

    ...

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
