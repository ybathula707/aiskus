import ollama
from ollama import Client
import pytest
import time
from aiskus_app.models.question import Question
from aiskus_app.clients.ollama_client import OllamaClient


    # question1=Question(question_body="What is the color of the moon?", question_asked_time=time.time())
    # question2=Question(question_body="Why does the moon look like different colors at different times?", question_asked_time=time.time())
    # question3=Question(question_body="I don't understand the phases of the moon", question_asked_time=time.time())
    # question_objects_array =[question1, question2, question3]
@pytest.fixture
def ollama_client():
    ollama_test_client= OllamaClient()
    yield ollama_test_client

def test_summary_request(ollama_client):
    question1=Question(question_body="What is the color of the moon?", question_asked_time=time.time())
    question2=Question(question_body="Why does the moon look like different colors at different times?", question_asked_time=time.time())
    question3=Question(question_body="I don't understand the phases of the moon", question_asked_time=time.time())
    question_objects_array =[question1, question2, question3]
    response = ollama_client.summary_request(question_objects_array)

    print(response.message.content)
    assert response.message.content == "Fail Purposely" 

def test_summary_realistic(ollama_client):
    question1 = Question(
        question_body="Why do we need to sort the array before using the two pointer method?",
        question_asked_time=time.time()
    )
    question2 = Question(
        question_body="How do we choose the starting positions for the left and right pointers?",
        question_asked_time=time.time()
    )
    question3 = Question(
        question_body="Why can't we just use a single loop instead of two pointers?",
        question_asked_time=time.time()
    )
    question4 = Question(
        question_body="I'm confused about when to move the left pointer versus the right pointer.",
        question_asked_time=time.time()
    )
    question5 = Question(
        question_body="How does the two pointer approach help avoid checking duplicate pairs?",
        question_asked_time=time.time()
    )
    question6 = Question(
        question_body="I don't understand how incrementing works with the two points. How do they not overlap?",
        question_asked_time=time.time()
    )
    question7 = Question(
        question_body="Is the two pointer method only for arrays, or can it be used on linked lists too?",
        question_asked_time=time.time()
    )
    question8 = Question(
        question_body="How is the two pointer method different from using recursion?",
        question_asked_time=time.time()
    )
    question9 = Question(
        question_body="I'm getting stuck in an infinite loop when using two pointers. What might cause that?",
        question_asked_time=time.time()
    )
    question10 = Question(
        question_body="Why do we need to increment the poointers in opposite directions",
        question_asked_time=time.time()
    )

    question_objects_array = [
        question1,
        question2,
        question3,
        question4,
        question5,
        question6,
        question7,
        question8,
        question9,
        question10,
    ]

    response = ollama_client.summary_request(question_objects_array)
    print(response.message.content)
    assert response.message.content == "Fail Purposely" 

