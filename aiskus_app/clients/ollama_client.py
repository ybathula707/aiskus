import ollama
from ollama import Client
from ..models.question import Question

question_prompt= """
                    Below is a list of questions asked by students who sitting in a lecture. I will send them to you as a list.
                    Carefully review all the questions and:
                    Identify and list the main themes or patterns behind the students' confusion. 

                    Summarize, in one paragraph, the knowledge gaps and difficulties these questions reveal about the students' understanding.
                    In a second paragraph, provide clear, practical advice for the teacher, specifying what concepts or explanations should be revisited or strengthened during the lecture.
                    Please format your response with the following structure:

                    Themes = [Theme 1, Theme 2, Theme 3 … ]
                    Summary of Knowledge Gaps & Advice to the Teacher: [Two paragraphs]

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
    