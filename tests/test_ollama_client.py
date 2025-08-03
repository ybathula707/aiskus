import ollama
from ollama import Client
import pytest
import json
import time
from aiskus_app.models.question import Question
from aiskus_app.models.summary import Summary
from aiskus_app.clients.ollama_client import OllamaClient


    # question1=Question(question_body="What is the color of the moon?", question_asked_time=time.time())
    # question2=Question(question_body="Why does the moon look like different colors at different times?", question_asked_time=time.time())
    # question3=Question(question_body="I don't understand the phases of the moon", question_asked_time=time.time())
    # question_objects_array =[question1, question2, question3]
@pytest.fixture
def ollama_client():
    ollama_test_client= OllamaClient()
    yield ollama_test_client

@pytest.fixture
def sample_metadata_list():
    """Create sample metadata that simulates what would come from the database"""
    metadata1 = {
        'id': 1,
        'themes': json.dumps(["two pointer method", "array sorting", "algorithm confusion"]),
        'summary_str': '(1) Students demonstrate fundamental gaps in understanding the two pointer technique, particularly struggling with pointer movement logic and the necessity of sorting arrays beforehand.\n(2) Instructors should provide more visual demonstrations of pointer movement, use step-by-step traced examples, and explain the relationship between sorting and the algorithm\'s correctness.\n(3) Students show high engagement but growing frustration with algorithmic thinking.'
    }
    
    metadata2 = {
        'id': 2,
        'themes': json.dumps(["loop optimization", "infinite loops", "pointer increment"]),
        'summary_str': '(1) Students are confused about loop termination conditions and proper pointer advancement, leading to infinite loops and incorrect algorithm implementation.\n(2) Teachers should focus on debugging strategies, provide flowchart representations of the algorithm, and emphasize testing with small examples.\n(3) Students appear overwhelmed but determined to understand the concept.'
    }
    
    metadata3 = {
        'id': 3,
        'themes': json.dumps(["data structures", "linked lists vs arrays", "algorithm application"]),
        'summary_str': '(1) There is confusion about when and where two pointer techniques can be applied, specifically regarding different data structures and their constraints.\n(2) Instructors should create a comparison chart of data structures, provide multiple use cases, and demonstrate adaptations of the technique.\n(3) Curious students seeking to understand broader applications beyond basic examples.'
    }
    
    return [metadata1, metadata2, metadata3]


def test_summary_request(ollama_client):
    question1=Question(question_body="What is the color of the moon?", question_asked_time=time.time())
    question2=Question(question_body="Why does the moon look like different colors at different times?", question_asked_time=time.time())
    question3=Question(question_body="I don't understand the phases of the moon", question_asked_time=time.time())
    question_objects_array =[question1, question2, question3]
    response = ollama_client.summary_request(question_objects_array)

    print(response.message.content)
    assert response.message.content is not None

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

    start =response.message.content.find('{')
    end =response.message.content.find('}') + 1

    if start != -1 and end != -1:
        cleaned = response.message.content[start:end]
        data=json.loads(cleaned)
        print(data)
    else:
        print("No JSON found")

    if data:
        summary_obj = Summary(first_question_time=data["first_question_time"],
                              last_question_time=data["last_question_time"],
                              themes=data["themes"],
                              summary=data["summary"],
                              queried=False)
        print("====Here is the batch summary: ====", summary_obj.summary)

    assert summary_obj.summary is not None 
    assert '(1)' in summary_obj.summary, "summary object missing (1) attribute"
    assert '(2)' in summary_obj.summary, "summary object missing (2) attribute"

def test_report_generated(ollama_client,sample_metadata_list ):

    response = ollama_client.create_report(sample_metadata_list)    
    content = response.message.content

    start = content.find('{')
    end = content.find('}') +1
    
    cleaned_response = json.loads(content[start:end])

    #Checking all required keys exist in the response 
    assert response is not None
    assert cleaned_response['summary'] is not None
    assert cleaned_response['number_of_questions'] is not None
    assert cleaned_response['themes'] is not None and type(cleaned_response['themes']) is list  
    assert cleaned_response['student_headspace'] is not None
    assert cleaned_response['generated_time'] is not None



