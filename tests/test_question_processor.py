import ollama
from ollama import Client
import pytest
import json
import time
from aiskus_app.models.question import Question
from aiskus_app.models.summary import Summary
from aiskus_app.clients.ollama_client import OllamaClient
from aiskus_app import create_app
from aiskus_app.services.questionProcessor import QuestionProcessor

@pytest.fixture
def ollama_client():
    ollama_test_client= OllamaClient()
    yield ollama_test_client
@pytest.fixture
def question_processor():
    yield QuestionProcessor()
    # check how to do this with app context

def test_q(ollama_client, question_processor):
    question1=Question(question_body="What is the color of the moon?", question_asked_time=time.time())
    x = question_processor.processQuestion(question1)
    assert x is "hello"
