from ollama import chat
from ollama import ChatResponse
from flask import Flask, request, jsonify
import time
from .models.question import Question
from .services.questionProcessor import QuestionProcessor

def create_app():

    # Instantiating a Flask as ' app'
    app = Flask(__name__)
    """
    setting up a singleton intance of the QuestionProcessor class for the lifecycle of the flask applicaition.
    Flask app will manage all questionsfed into the app, through a single processor. 
    This will help retain session context within the runitime of the model, across batches of messages. 
    Question is there a way to wipe the context of the model between sessions?

    Think: can we use cookies at this point of logic,  in order to build a future feature on the client that
    requires persisted information
    
    """
    app.session_question_processor = QuestionProcessor()

    @app.route('/')
    def main():

        sample_question= Question(
            question_body="What is a cucumber? Describe the growing season 5 sentences.",
            question_asked_time=time.time())
        # Delaring a response of type ChatResponse, setting it equal to what the chat function returns
        # look into chat response tupe, and chat function, with syntax of the messages attribute
        response: ChatResponse = chat(model='gemma3n:e4b', messages=[
            {'role':'user',
            'content': sample_question.question_body
            },
        ])

        summary_response: ChatResponse = chat(model='gemma3n:e4b', messages=[
            {'role':'user',
            'content': 'What is the summary of the following text. Tell me the main points, in one sentence' +
            response.message.content
            },
        ])
        # #print the content attribute of the message attribute of the response
        # print(response['message']['content'])
        # #printing the content of the message
        # print(response.message)

        # print(response)
        answer = summary_response.message.content
        # return f"<p> Your cucumber summary is {answer}.+The original response was {response.message.content}. Detail {sample_question.__repr__()}</p>"
        return f"<h> Detail {sample_question.__repr__()}</h>"

    @app.route('/ask', methods=['POST'])
    def audience_ask():

        """
            Extract the JSON from the response object. I can deserialize & validate with pydantic if necessary (later)
            Returning 400 bad req if request was malformed due to missing data or null request. 
        """
        try:
            question_body_str = request.form['question_body']
            if not question_body_str:
                return jsonify({"status": "failure",
                                "message": "malformed or missing request",
                                "error" : f"{e}"}), 400
            
            """ 
            Yoshi Business logic Note
                create a question object using the sent_question param, assig it to 'question_body' 
                attribute of a Question class object.

                We make the Question object here, then send it to out to teh messageProcessor instance object.
                the messageProcessor object will be the single object, used to process all quesitons 
                for length of the aiskus session.

                Return 200 Success once question object gets sent to processor

                Need custom exceptions later
            """
    
            questionObject : Question =  Question(question_body=question_body_str,question_asked_time=time.time())
            app.session_question_processor.processQuestion(questionObject)
            return jsonify({"status": "success",
                            "message": "question queued to be processed"}), 200
        except Exception as e:
            return jsonify({"status": "failure",
                            "message": "question unable to be processed",
                            "error" : f"{e}"}), 500
    
    return app

