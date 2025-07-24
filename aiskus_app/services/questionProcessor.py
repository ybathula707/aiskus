from ..models.question import Question
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
        return
    
    def processQuestion(self,question: Question):

        try: 
            self.batch_questions.append(question)
            print(f"Questions received: {len(self.batch_questions)}")
            self.batch_body += f"Question: {question.question_body}, " 
            self.batch_body += f", Question: {question.question_body}"
            print(f"batched messages: {self.batch_body}")
            #once batch size is around 10, we send the array to the Ollama Client liek:
            #Ollama_Client
            return
        except Exception as e:
            print(f"Error receiving message {e}")
            return



"""
Need algorithm to set batch size based on classroom size.
Idea: prompt teacher for class size and then allocate the batch size based on optimal.
Maybe this can be customizable in the future:
Teacher can set their own preferred batch size.
"""