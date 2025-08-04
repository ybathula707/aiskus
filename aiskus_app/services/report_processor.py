from aiskus_app.db import get_db, close_db
from flask import jsonify, current_app
from aiskus_app.models.summary import Summary
import json

class ReportProcessor:
    
    def generate_report(self,request_time):
        '''
            Receives request time, queries DB to get the unprocessed summaries since last report.
            Parses the rows into the metadata format for Ollama client.
            returns the report to the endpoint. 
            
        '''
        if not request_time:
            raise ValueError("Invalid timestamp provided. Internal Error.")

        try:

            # need to implement DB manager. This aint scalable sis. 
            # TODO: Seperate DB concerns
            db_connection = get_db()
            if not db_connection:
                raise ConnectionError("Couldn't connect to DB. Internal Error.")

            
            rows = self._get_unprocessed_summaries(db_connection, request_time)
            if not rows:
                return {"message": "No new summaries to process", "report": {}}
            
            metadata_list = self._transform_rows_to_metadata(rows)
            raw_report = current_app.session_ollama_client.create_report(metadata_list)
            fronted_usable_json_report = self._parse_to_json(raw_report)

        except Exception as e:
            raise SystemError(f"Unable to generate report. Internal Error {e}")
        
        return {"report" :fronted_usable_json_report}

        
    
    def _get_unprocessed_summaries(self,conn, request_timestamp):
        #TODO: update w/ DB manager. Terrible practice to do it w/ connection manager
        """
        Select rows from themes_and_summaries where:
        - first_question_time is before the request timestamp
        - queried is False (0)
        
        Args:
            conn: SQLite database connection
            trequest_timestamp: Unix timestamp to filter by
            
        Returns:
            List of rows matching the criteria
        """
        cursor = conn.cursor()
        
        query = """
        SELECT id, themes, summary_str, queried
        FROM themes_and_summaries 
        WHERE first_question_time < ? AND queried = 0
        ORDER BY first_question_time DESC;
        """
        
        cursor.execute(query, (request_timestamp, ))
        rows = cursor.fetchall()
    
        return rows

    def _transform_rows_to_metadata(self, rows):
        """
            Models are optimized to process json-like objects. Converting rows to a dictionary 
            of metadata will optimize performance of the ollama client interaction w/ model.
        """
        if rows is None:
            return #validate in calling function that this doesn't happen. If rows is empty, no reports generated.
        metadata_list = []
        try:
            for row in rows:
                row_metadata ={'id' : row['id'],
                            'themes': row['themes'],
                            'summary_str': row['summary_str']}
                metadata_list.append(row_metadata)
        except (KeyError, TypeError) as e:
                raise ValueError(f"Unable to process report {e}")
        except Exception as e:
                raise SystemError(f"Unable to process report {e}")

        return metadata_list
    

    def _parse_to_json(self,ollama_response):
        try:
            contents = ollama_response.message.content
            if not contents:
                raise ValueError("No response contents from Ollama client")
            
            start = contents.rfind('{')
            end = contents.rfind('}') + 1
                
            if start == -1 or end == 0:
                raise ValueError("No valid JSON found in Ollama response")

            cleaned_response = json.loads(contents[start:end])

            return cleaned_response
        except Exception as e:
            raise SystemError(f"Failed to parse Ollama response: {e}")
        
#TODO implement this
def set_queried_true(row):
    pass