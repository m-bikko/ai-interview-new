import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Get absolute paths to directories
    project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    instance_dir = os.path.join(project_dir, 'instance')
    uploads_dir = os.path.join(project_dir, 'uploads')
    static_uploads_dir = os.path.join(project_dir, 'static', 'uploads')
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', f'sqlite:///{os.path.join(instance_dir, "ai_interview.db")}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = uploads_dir
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
    
    # Ensure directories exist
    os.makedirs(instance_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(static_uploads_dir, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Register blueprints
    from src.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from src.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from src.catalog import catalog as catalog_blueprint
    app.register_blueprint(catalog_blueprint)
    
    from src.interviews import interviews as interviews_blueprint
    app.register_blueprint(interviews_blueprint)
    
    from src.cv import cv as cv_blueprint
    app.register_blueprint(cv_blueprint)
    
    from src.profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint)
    
    # Create database on first run
    with app.app_context():
        db.create_all()
    
    return app