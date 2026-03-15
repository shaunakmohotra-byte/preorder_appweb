from flask import Flask
from .store import init_default_data
import os
from flask import Flask
def create_app():
    # Tell Flask the template folder is one level up from this file
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.abspath(os.path.join(base_dir, '..', 'static'))
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)    
    app.config['SECRET_KEY'] = 'dev-secret-key-123'
   
    # Ensure JSON files exist before the app starts
    init_default_data()

    # Register Blueprints
    from .routes import bp as main_bp
    from .auth import bp as auth_bp
    from .admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
