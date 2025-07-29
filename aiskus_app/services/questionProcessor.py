from ..models.question import Question
from ..clients.ollama_client import OllamaClient
from ..models.summary import Summary
from aiskus_app.db import get_db, close_db
import json


class QuestionProcessor:

# shoudl the QuestionProcessor class have its own instance of ollama_clent?
# The questions may build on eachother, so it makes sense if each insance object question processor worked 
# with only one ollama client. 
# If this is the case, in he case we wnat a single Ollama_client to retail question context between batches
# do we need to declare ollama client as s ingleton object in the create_app? Or should it be declared only
# in this file, since client will onyl be used here? For context, factory has singleton inctance of QuesitonProcessor laready.
    def __init__(self):
        self.batch_questions = []
        self.batch_body:str = ""
        self.ollama_client = OllamaClient()
        return
    
    '''
        Append question into batch array.
        
    '''
    
    def processQuestion(self,question: Question):

        try: 
            response = ""
            summary_obj = None
            print(question)
            self.batch_questions.append( f'student question & ask time: {question}')
            #once batch size is around 10, we send the array to the Ollama Client liek:
            #Ollama_Client
            
            if len(self.batch_questions) >= 10:

                response=self.ollama_client.summary_request(self.batch_questions)
                # print("==========")
                # print(response)
                # print("==========")

                contents = response.message.content

                if not contents:
                   raise Exception
                   
                
                if contents:
                    start = contents.find('{')
                    end = contents.find('}') + 1
                    cleaned_data = json.loads(contents[start:end])
                    summary_obj=Summary(first_question_time=cleaned_data['first_question_time'],
                                        last_question_time=cleaned_data['last_question_time'],
                                        themes=cleaned_data['themes'],
                                        summary=cleaned_data['summary'],
                                        queried=False)
                print(f"batched messages: {self.batch_questions}")
            
                '''
                    Get the DB,
                    use cursor to insert into themes_and_summaries

                '''
                db = get_db()
                cursor = db.cursor()

                cursor.execute(
                    """ 
                    INSERT INTO themes_and_summaries 
                    (first_question_time, last_question_time, themes_json, summary_str, queried)
                    VALUES(?,?,?,?,?)
                    """,
                    (summary_obj.first_question_time, 
                     summary_obj.last_question_time, 
                     json.dumps(summary_obj.themes), 
                     summary_obj.summary, 
                     0)

                )
                db.commit()
                c = cursor.execute(
                    "SELECT summary_str FROM themes_and_summaries WHERE queried = ?", (0,)
                    )

                row = c.fetchone()
                print(f"Inserted row: {row['summary_str']}")

                cursor.close()     # Always explicitly close cursor
                close_db()         # You can explicitly close; if inside a Flask request, teardown should do this
                self.batch_questions.clear()

            #self.batch_questions.clear()
            return summary_obj
            
        except Exception as e:
            print(f"Error receiving message {e}")
            return





"""
Need algorithm to set batch size based on classroom size.
Idea: prompt teacher for class size and then allocate the batch size based on optimal.
Maybe this can be customizable in the future:
Teacher can set their own preferred batch size.
"""