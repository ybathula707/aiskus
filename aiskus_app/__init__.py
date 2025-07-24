import os
from flask import Flask
from .services.questionProcessor import QuestionProcessor



def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
            DATABASE="instance/themes_and_summaries.sqlite3"
        )
    
    #registering db in application instance using db helper method 
    from . import db
    db.init_app(app)

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


    return app

