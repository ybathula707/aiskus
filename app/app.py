from ollama import chat
from ollama import ChatResponse
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def main():
    # Delaring a response of type ChatResponse, setting it equal to what the chat function returns
    # look into chat response tupe, and chat function, with syntax of the messages attribute
    response: ChatResponse = chat(model='gemma3n:e4b', messages=[
        {'role':'user',
        'content': 'What is a cucumber and what color are they, typically? Describe the texture.'
        'Keep the response short, to exactly 5 sentences.'
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
    return f"<p>HELLO THERE, I'VE BEEN WAITING FOR YOU!!! Your cucumber summary is {answer}. The original response was {response.message.content}</p>"

# if __name__ == '__main__':
#     main()