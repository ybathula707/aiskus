from ..models.question import Question
from ..clients.ollama_client import OllamaClient
from ..models.summary import Summary
from aiskus_app.db import get_db, close_db
from flask import current_app
import json


class QuestionProcessor:

# shoudl the QuestionProcessor class have its own instance of ollama_clent?
# The questions may build on eachother, so it makes sense if each insance object question processor worked 
# with only one ollama client. 
# If this is the case, in he case we wnat a single Ollama_client to retail question context between batches
# do we need to declare ollama client as s ingleton object in the create_app? Or should it be declared only
# in this file, since client will onyl be used here? For context, factory has singleton inctance of QuesitonProcessor laready.

#todo REFACTOR
    def __init__(self):
        self.batch_questions = []
        self.batch_body:str = ""
        return

    """
        Decouple / find smart way to combine
        processQuestion =>> batchProcessQuestion process based on batch size
        processTeacherReportReq => process batch questions as is.
        process

        seperate out. helper funcs:
        - insert into array
        - func to check batch size from teacher (later)
        - func parse response form ollama
        - create summary object? 
        - func execute db interaction

    
    """
    def processQuestion(self,question: Question):

        if question.question_body is None or "":
            raise ValueError("Empty question body will not be processed")

        try: 
            self.batch_questions.append( f'student question & ask time: {question}')

            #sending batch to Ollama client
            if len(self.batch_questions) >= 10:
                response=current_app.session_ollama_client.summary_request(self.batch_questions)
                response_contents = response.message.content

                if not response_contents:
                   raise ValueError("Empty response froom ollama client")
                   
                
                cleaned_data=self.__parse_to_json(response_contents)
                summary_object=Summary(first_question_time=cleaned_data['first_question_time'],
                                        last_question_time=cleaned_data['last_question_time'],
                                        themes=cleaned_data['themes'],
                                        summary=cleaned_data['summary'],
                                        queried=False)
                    
                print(f"batched messages: {self.batch_questions}")
                current_app.logger.info(f"Batched messages {self.batch_questions}")


                db = get_db()
                if not db:
                    raise ConnectionError("Couldn't connect to DB. Internal Error.")

                self._insert_batched_summary_object_db(db, summary_object)

                print(f"Current Summary: {summary_object.summary}")

                self.batch_questions.clear() #only done if db interactions went okay

                 #self.batch_questions.clear()
                return summary_object  # TODO: don'tt think we need to return anything anymore
            
        except Exception as e:  #more robust handling. SHould raise instead
            raise SystemError(f"Error receiving message {e}")




    def _insert_batched_summary_object_db(self, db_conn, summary_object: Summary) -> None:
        """
            Receives a db connection object. Calls cursor on the connection to execute the insertion query
            Raises system error in case anything with DB goes wrong.
        """
        #todo should use DB manager for connection validetion
        try:
            cursor = db_conn.cursor()   
            cursor.execute(
                        """ 
                        INSERT INTO themes_and_summaries 
                        (first_question_time, last_question_time, themes, summary_str, queried)
                        VALUES(?,?,?,?,?)
                        """,
                        (summary_object.first_question_time, 
                        summary_object.last_question_time, 
                        json.dumps(summary_object.themes), 
                        summary_object.summary, 
                        0)

                    )
            db_conn.commit()
            cursor.close()
            close_db()
            
        except Exception as e:
            raise SystemError(f"Unable to execute on DB {e}")
        

    def __parse_to_json(self, ollama_message_contents) -> any:

        start = ollama_message_contents.find('{')
        end = ollama_message_contents.find('}') + 1
        cleaned_response = json.loads(ollama_message_contents[start:end])

        return cleaned_response


"""
Need algorithm to set batch size based on classroom size.
Idea: prompt teacher for class size and then allocate the batch size based on optimal.
Maybe this can be customizable in the future:
Teacher can set their own preferred batch size.
"""