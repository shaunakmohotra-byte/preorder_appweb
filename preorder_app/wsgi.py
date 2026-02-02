import os
from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix

app = create_app()

# ---------------------------------------------------------
# CRITICAL FIX FOR RENDER DEPLOYMENT
# This tells Flask it is behind a proxy (Render) so it
# correctly handles HTTPS and preserves POST requests.
# ---------------------------------------------------------
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if __name__ == "__main__":
    app.run()
