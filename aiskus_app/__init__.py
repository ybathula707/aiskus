import os
from flask import Flask
import atexit
import signal
from .services.question_processor import QuestionProcessor
from .services.report_processor import ReportProcessor
from .clients.ollama_client import OllamaClient
import webbrowser
from threading import Timer

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
            DATABASE="instance/themes_and_summaries.sqlite3"
        )
    app.logger.info(f"App configuration: {app.config}")

    os.makedirs(app.instance_path, exist_ok=True)
    
    #registering db in application instance using db helper method 
    from . import db
    db.init_app(app)

    # Run database initialization automatically at startup
    with app.app_context():
        try:
            db.init_db()
            app.logger.info("Database initialized on startup.")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")
             

    app.session_question_processor = QuestionProcessor()
    app.session_report_processor = ReportProcessor()
    app.session_ollama_client = OllamaClient()

    from .api.student import student_aiskus_bp
    app.register_blueprint(student_aiskus_bp)

    from .api.teacher import teacher_aiskus_bp
    app.register_blueprint(teacher_aiskus_bp)

    """
    setting up a singleton intance of the QuestionProcessor class 
    and report processor class for the lifecycle of the flask applicaition object.
    
    Flask app object will manage all questions fed into the app, through a single processor. 
    This will help retain session context within the runitime of the model, across batches of messages. 
    Question is there a way to wipe the context of the model between sessions?

    Flask will manage all report requests coming into the app via the same
    instance as well.
    
    """
    
    webbrowser.open_new('http://127.0.0.1:5001/')

    # Register cleanup functions
    def cleanup_app():
        """Cleanup function called on app shutdown."""
        app.logger.info("Starting application cleanup...")

        try:
            # Clean up processors if they have cleanup methods
            if hasattr(app.session_question_processor, 'cleanup'):
                app.session_question_processor.cleanup()
            
            if hasattr(app.session_report_processor, 'cleanup'):
                app.session_report_processor.cleanup()
            
            if hasattr(app.session_ollama_client, 'cleanup'):
                app.session_ollama_client.cleanup()
            
            # Close database connections
            if hasattr(db, 'close_db'):
                with app.app_context():
                    db.close_db()
            
            app.logger.info("Application cleanup completed")
            
        except Exception as e:
            app.logger.error(f"Error during cleanup: {e}")
    
    # Register cleanup for different shutdown scenarios
    atexit.register(cleanup_app)
    
    # TODO: (Docker/Kubernetes
    def signal_handler(signum, frame):
        app.logger.info(f"Received signal {signum}, shutting down gracefully...")
        cleanup_app()
        exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
 
    return app

