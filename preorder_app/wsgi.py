import app
from app import create_app

# Initialize the Flask application
app = create_app()

if __name__ == "__main__":
    app.run()
