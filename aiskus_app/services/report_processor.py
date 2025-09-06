from aiskus_app.db import get_db, close_db
from flask import jsonify, current_app
from aiskus_app.models.summary import Summary
import json
from pydantic import BaseModel, ConfigDict, ValidationError
import re
class SummaryReport(BaseModel):
    model_config=ConfigDict(strict=True) # Config dict is used to configure pydantic behavior
    summary: str
    themes: list[str]
    number_of_questions: int
    student_headspace: str

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

            # need to implement DB manager. This aint scalable 
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
            print(type(fronted_usable_json_report))
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
            print(f"Content of summaries {contents}")
            # Extract JSON from the response using multiple strategies
            json_content = self._extract_json_from_response(contents)
            
            if not json_content:
                raise ValueError("No valid JSON found in response")
            
            #Use pydantic to 1)Validate the extracted json from response 2) Reutrn it as a dictionary to calling function
            #Jsonify in the endpoint iteself hanfles converiting this to proper JSON format
            validated_response= SummaryReport.model_validate_json(json_content)
            json_response_dict= SummaryReport.model_dump(validated_response)
            print(f"Content of validated summary {json_response_dict}")
            return json_response_dict

        except ValidationError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to parse Ollama response: {e}")
            
    def _extract_json_from_response(self, content: str):
        """
        Extract JSON from response content using multiple strategies.
        Handles nested JSON, markdown code blocks, and embedded JSON.
        """
        
        # Strategy 1: Look for JSON in markdown code blocks
        json_code_block = re.search(r'``````', content, re.DOTALL)
        if json_code_block:
            return json_code_block.group(1).strip()
        
        # Strategy 2: Look for any code block that might contain JSON
        code_block = re.search(r'``````', content, re.DOTALL)
        if code_block:
            potential_json = code_block.group(1).strip()
            if self._is_valid_json(potential_json):
                return potential_json
        
        # Strategy 3: Find JSON objects using balanced brace matching
        json_objects = self._extract_balanced_json_objects(content)
        for json_obj in json_objects:
            if self._is_valid_json(json_obj):
                return json_obj
        
        # Strategy 4: Try the entire content as JSON
        if self._is_valid_json(content.strip()):
            return content.strip()
        
        return None

    def _extract_balanced_json_objects(self, content: str) -> list:
        """
        Extract JSON objects using balanced brace matching.
        Handles nested objects properly.
        """
        json_objects = []
        brace_count = 0
        start_pos = -1
        
        for i, char in enumerate(content):
            if char == '{':
                if brace_count == 0:
                    start_pos = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_pos != -1:
                    # Found a complete JSON object
                    json_candidate = content[start_pos:i+1]
                    json_objects.append(json_candidate)
                    start_pos = -1
        
        return json_objects

    def _is_valid_json(self, text: str) -> bool:
        """Check if a string is valid JSON"""
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
        #TODO implement this

    def set_queried_true(row):
        pass