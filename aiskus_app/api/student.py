from flask import (request, Blueprint, render_template, abort, jsonify, current_app)
from jinja2 import TemplateNotFound
from ..models.question import Question
import time


#student blueprint 
#/POST ask endpoint
student_aiskus_bp= Blueprint('student_aiskus_page', __name__, template_folder='/static/student')
@student_aiskus_bp.route('/aiskus/ask', methods=['POST'])
def post_question():
    """
    Extract JSON from response object attribute question_body
    Return 400 if req was malformed due to missing data or null request
    """
    try:
        question_body_str= request.form("question_body")
        if not question_body_str:   
            return jsonify({"status": "failure",
                            "message": "malformed question body",
                            "error": f"{e}",}), 400
        student_question=Question(question_body=question_body_str, question_asked_time=time.time())
        current_app.session_question_processor.processQuestion(student_question)

        return jsonify({"status": "success",
                        "message": "message queued successfully",
                        }), 200
    except Exception as e:
        return jsonify({"status": "internal failure",
                        "message": "Question unable to be processe dat this time",
                        "arror": f"{e}" }), 500
    


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
    