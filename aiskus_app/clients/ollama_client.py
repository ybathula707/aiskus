import ollama
from ollama import Client
from ..models.question import Question

question_prompt= """
                    1. Identify and list the main themes or patterns behind the students' confusion. Your themes should concisely communicate overlapping patterns if they exist.

                    2. Provide a summary as a single string containing exactly two paragraphs:

                    - The first paragraph (tagged with "(1)") should summarize the knowledge gaps and difficulties revealed by the questions.  
                    - The second paragraph (tagged with "(2)") should provide clear and practical advice for the teacher on which concepts or explanations to revisit or strengthen during the lecture.  

                    **Each paragraph must start with its tag "(1)" or "(2)" exactly, and the two paragraphs should be separated by a newline character inside the single string.**  
                    For example:

                    "(1) This paragraph summarizes the knowledge gaps...  
                    (2) This paragraph gives advice to the teacher..."

                    3. Return the full response strictly as a JSON object with the following keys and value types:
                    first_question_time = first_question_time
                    last_question_time = last_question_time
                    themes = themes array list
                    summary = the two paragraphs as one string 
                    

                    I will also be providing to you chat context in the form of a message history, which contains previous user
                    queries, along with assistant responses. Please use the message history to provide accurate responses that
                    are tialored to previous discussions witht he assitant. This can look like capturing recurring gaps in knowledge between
                    prompts. 

                    Here are the student questions & context:


                """

class OllamaClient:

    def __init__(self, loaclhost='http://localhost:11434'):
        self.ollama_client_object = Client(host=loaclhost)
        self.message_history = []

    """
    send_request
    Parameters: list of batched question obhects from the question processor

    Receives the list of questions. Sends them in a chat to the model, along with the prompt:
        - prompt goals:
            - extract themes

    
    """

    def summary_request (self,batched_messages: list[Question]):
        question_input = question_prompt + str(batched_messages)
        response = self.ollama_client_object.chat(
            model='gemma3n:e4b', 
            messages=[{'role': 'user','content': self.message_history},
                      {'role': 'user', 'content': question_input}
                    ]
            )
        
        # adding the model response to the memory
        self.message_history += [
            {'role':'user','content':question_input},
            {'role': 'assistant', 'content': response.message.content},
        ]

        return response
    