from flask import (
    Blueprint, Flask,jsonify, flash, g, redirect, render_template, request, url_for, current_app
)
from ollama import chat
from ollama import ChatResponse
import time
from werkzeug.exceptions import abort
from ..models.question import Question
from ..db import get_db

bp = Blueprint('ask', __name__)
@bp.route('/')
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

@bp.route('/ask', methods=['POST'])
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
        current_app.session_question_processor.processQuestion(questionObject)
        return jsonify({"status": "success",
                        "message": "question queued to be processed"}), 200
    except Exception as e:
        return jsonify({"status": "failure",
                        "message": "question unable to be processed",
                        "error" : f"{e}"}), 500
    

# @bp.route('/summaries/latest', methods=['GET'])
# def teacher_summaries():
    
