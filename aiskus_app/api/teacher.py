from flask import (request, Blueprint, render_template, abort, jsonify, current_app)
import json
# teacher summaries
# GET/SUMMARIES/LATEST

teacher_aiskus_bp= Blueprint("teacher_aiskus_page", __name__, template_folder='teacher/request_report_page.html')

@teacher_aiskus_bp.route("/aiskus/teacher/live-summaries")
def teacher_home():
    return render_template('teacher/request_report_page.html')

@teacher_aiskus_bp.route('/aiskus/teacher/pre-lecture')
def teacher_pre_lecture():
    return render_template('teacher/pre_lecture.html')

@teacher_aiskus_bp.route("/aiskus/teacher/qr")
def qr_code_page():
    return render_template('teacher/qr.html')

@teacher_aiskus_bp.route('/get/summaries/latest', methods=['GET'])
def get_latest_summaries():

    try:
        
        request_time = request.args.get('timestamp')
        if not request_time:
            return jsonify({
                "status": "error",
                "message": "timestamp parameter required"
            }), 400
        
        report = current_app.session_report_processor.generate_report(request_time)
        
        return jsonify({
            "status": "success",
            **report,
            }), 200
    
    except ValueError as e:
        current_app.logger.error(f"Processing error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    
    except SystemError as e:
        current_app.logger.error(f"Processing error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"{e}"}
            ), 500
    
    except Exception as e:
        current_app.logger.error(f"Unknown error: {str(e)}")
        return jsonify({""
            "status": "internal failure",
            "message": "failed to get latest report",
            "error": f"{e}"
            }), 500
    

    #returns Json object
    '''
    # make a summary request object using current time
    # Or just call Summary_processor with request time

    return summary_report_object

    Frontend takes summary_report_object and displays it 
    Or maybe just return row from db with selected rows, 

    Summary processor; 
    Make call to db to get relevant rows
    reuturn the themes and summaries as an json?
         make a csll to ollama again to summarize teh avg of all summaries?
         maybe for sake of mvp just diplay it all
    return teh array to frontend, whihc will display it. 


    '''
    pass