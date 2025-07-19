from ..models.question import Question
class QuestionProcessor:

    def __init__(self):
        self.batch_questions = []
        self.batch_body:str = f""
        return
    
    def processQuestion(self,question: Question):

        try: 
            self.batch_questions.append(question)
            print(f"Questions received: {len(self.batch_questions)}")
            self.batch_body + f"Question: {question.question_body}" 
            print(f"batched messages: {self.batch_body}")
            return
        except Exception as e:
            print(f"Error receiving message {e}")
            return



