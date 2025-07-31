import os
from flask import Flask
from .services.questionProcessor import QuestionProcessor


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
            DATABASE="instance/themes_and_summaries.sqlite3"
        )
    # Ensure instance folder exists
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
    """
    setting up a singleton intance of the QuestionProcessor class for the lifecycle of the flask applicaition object.
    Flask app object will manage all questions fed into the app, through a single processor. 
    This will help retain session context within the runitime of the model, across batches of messages. 
    Question is there a way to wipe the context of the model between sessions?

    Think: can we use cookies at this point of logic,  in order to build a future feature on the client that
    requires persisted information
    
    """

    from .blueprints import ask
    app.register_blueprint(ask.bp)
    app.add_url_rule('/', endpoint='index')

    from .api.student import student_aiskus_bp
    app.register_blueprint(student_aiskus_bp)



    return app

