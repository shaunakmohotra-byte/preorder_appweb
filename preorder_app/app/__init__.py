import os
from flask import Flask

def create_app():
    app = Flask(__name__) # <--- Add 4 spaces before this line
    app.config['SECRET_KEY'] = '    asdasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdf' # <--- And this one
    
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
    # register blueprints
    # DO NOT FORGET THIS LINE
    app.config['SECRET_KEY'] = 'your-secret-key-here' 
    
    # ... rest of your code
    from .routes import bp as main_bp
    from .auth import bp as auth_bp
    from .admin import bp as admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # ensure data dir and default data
    from .store import init_default_data
    init_default_data()
    return app
