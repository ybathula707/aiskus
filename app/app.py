from ollama import chat
from ollama import ChatResponse
from flask import Flask, request, jsonify
import time
from .models.question import Question
app = Flask(__name__)

@app.route('/')
def main():

    sample_question= Question(
        question_body="What is a cucumber? Describe the growing season 5 sentences.",
        question_asked_time=time.time())
    # Delaring a response of type ChatResponse, setting it equal to what the chat function returns
    # look into chat response tupe, and chat function, with syntax of the messages attribute
    response: ChatResponse = chat(model='gemma3n:e4b', messages=[
        {'role':'user',
        'content': sample_question.question_body
        },
    ])

    summary_response: ChatResponse = chat(model='gemma3n:e4b', messages=[
        {'role':'user',
        'content': 'What is the summary of the following text. Tell me the main points, in one sentence' +
        response.message.content
        },
    ])
    # #print the content attribute of the message attribute of the response
    # print(response['message']['content'])
    # #printing the content of the message
    # print(response.message)

    # print(response)
    answer = summary_response.message.content
    # return f"<p> Your cucumber summary is {answer}.+The original response was {response.message.content}. Detail {sample_question.__repr__()}</p>"
    return f"<h> Detail {sample_question.__repr__()}</h>"

# if __name__ == '__main__':
#     main()